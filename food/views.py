from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, mixins, viewsets, views, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from .serializers import *
from authentication.serializers import ProfileSerializers
from django.db.models import Q


class MenuView(generics.GenericAPIView, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    # Mixin is inherited for generating Pagination for menu items
    # next & previous link is provided by this
    queryset = Menu.objects.all().order_by('id')
    serializer_class = MenuSerializer
    lookup_field = "id"

    def get(self, request, id=None):
        # If an item id is passed in parameter. Then, only details of that item will be fetched
        if id:
            return self.retrieve(request)
        else:
            return self.list(request)


class MyCart(viewsets.ViewSet):
    # Fetching API for items added in cart for currently logged-in user.
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def list(self, request):
        query = Cart.objects.filter(customer=request.user.profile)
        serializers = CartSerializers(query, many=True)
        all_data = []
        for cart in serializers.data:
            # Joining fields of two models
            cart_product = CartProduct.objects.filter(cart=cart['id'])
            cart_product_serializer = CartProductSerializers(
                cart_product, many=True)
            cart["cartproduct"] = cart_product_serializer.data
            all_data.append(cart)
        return Response(all_data)


class AddToCart(views.APIView):
    # Adding Menu Items to Cart
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        menu_id = request.data['id']
        menu_obj = Menu.objects.get(id=menu_id)
        # Filtering the cart of logged-in customer where product of that cart is not ordered yet.
        cart_cart = Cart.objects.filter(customer=request.user.profile).filter(complete=False).first()

        try:
            # If requested user already has a cart
            if cart_cart:
                # Reverse querying to find out if the cart belongs to any added items,
                # which is CartProduct model
                this_menu_in_cart = cart_cart.cartproduct_set.filter(menu=menu_obj)

                if this_menu_in_cart.exists():
                    # If the cart is already existed that means customer has already added this items
                    # So, Only updating the quantity and price of that item
                    cart_product_uct = CartProduct.objects.filter(menu=menu_obj).filter(cart__complete=False).first()
                    cart_product_uct.quantity += 1
                    cart_product_uct.subtotal += menu_obj.price
                    cart_product_uct.save()
                    cart_cart.total += menu_obj.price
                    cart_cart.save()
                else:
                    # If the added items doesn't belong to logged-in users cart,
                    # Then, it is added to that cart
                    cart_product_new = CartProduct.objects.create(
                        cart=cart_cart,
                        price=menu_obj.price,
                        quantity=1,
                        subtotal=menu_obj.price
                    )
                    cart_product_new.menu.add(menu_obj)
                    cart_cart.total += menu_obj.price
                    cart_cart.save()
            else:
                # If user doesn't have any cart, the initially a blank cart is created
                Cart.objects.create(
                    customer=request.user.profile,
                    total=0,
                    complete=False
                )
                # Object of newly created blank cart is created
                new_cart = Cart.objects.filter(customer=request.user.profile).filter(complete=False).first()
                # Now updating that cart as per id of requested item
                cart_product_new = CartProduct.objects.create(
                    cart=new_cart,
                    price=menu_obj.price,
                    quantity=1,
                    subtotal=menu_obj.price
                )
                cart_product_new.menu.add(menu_obj)
                new_cart.total += menu_obj.price
                new_cart.save()

            response_msg = {"error": False, "message": "Product is added to cart"}

        except:
            response_msg = {"error": True, "message": "Product is not added to cart !! Try Again"}

        return Response(response_msg)


class IncreaseCart(views.APIView):
    # Increasing the item quantity of the requested cart
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def post(self, request):
        cart_product_id = request.data["id"]
        cart_product = CartProduct.objects.get(id=cart_product_id)
        cart_obj = cart_product.cart

        cart_product.quantity += 1
        cart_product.subtotal += cart_product.price
        cart_product.save()

        cart_obj.total += cart_product.price
        cart_obj.save()

        return Response({"message": "Cart Product is Added"})


class DecreaseCart(views.APIView):
    # Decreasing the item quantity of the requested cart
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def post(self, request):
        cart_product_id = request.data["id"]
        cart_product = CartProduct.objects.get(id=cart_product_id)
        cart_obj = cart_product.cart

        cart_product.quantity -= 1
        cart_product.subtotal -= cart_product.price
        cart_product.save()

        if cart_product.quantity == 0:
            cart_product.delete()

        cart_obj.total -= cart_product.price
        cart_obj.save()

        return Response({"message": "Cart Product is Decreased"})


class DeleteCartProduct(views.APIView):
    # Deleting an item from the cart
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def post(self, request):
        cart_product = CartProduct.objects.get(id=request.data['id'])
        cart_obj = cart_product.cart
        # subtracting the values of previous item price from total price
        cart_obj.total -= cart_product.subtotal
        cart_obj.save()
        cart_product.delete()

        return Response({"message": "cart Product is deleted"})


class DeleteFullCart(views.APIView):
    # Deleting the full cart
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def post(self, request):
        try:
            cart_id = request.data['id']
            cart_obj = Cart.objects.get(id=cart_id)
            cart_obj.delete()
            response_msg = {"error": False, "message": "cart is Deleted"}
        except:
            response_msg = {"error": False, "message": "cart is Deleted"}

        return Response(response_msg)


class AlreadyAddedProductResponse(views.APIView):
    # Check every product from the cart
    # Required for getting updated about currently added items
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def post(self, request):
        data = request.data
        cartId = data["cartId"]
        menuId = data["menuId"]
        query = CartProduct.objects.filter(cart_id=cartId, menu=menuId)

        if query.exists():
            serializer = CartProductSerializers(query, many=True)
            response_msg = {"status": True, "cartdata": serializer.data}
            return Response(response_msg)
        else:
            response_msg = {"status": False, "cartdata": None}
            return Response(response_msg)


class RatingView(viewsets.ViewSet):
    # Rating API for each Menu Item
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def list(self, request):
        # Querying the rating situation for logged-in user
        query = Rating.objects.filter(customer=request.user.profile).order_by('-id')
        serializer = RatingSerializers(query, many=True)
        return Response(serializer.data)

    def create(self, request):
        try:
            # Rating an item when it wasn't rated before
            data = request.data
            customer_obj = request.user.profile
            rating_score = data['rating']
            menuId = data['menuId']
            menu_obj = Menu.objects.get(id=menuId)
            # Creating a rating field as per customer rating
            Rating.objects.create(
                customer=customer_obj,
                ratingScore=rating_score,
                menuName=menu_obj
            )
            # Now, object of Rating as per provided menu Id is created
            query = Rating.objects.filter(menuName=menu_obj)
            # Here, every rating of that item is added to the sum
            sum = 0
            for i in range(query.count()):
                rating = getattr(query[i], "ratingScore")
                sum += rating
            # Now, a mean value is created by dividing it with its total occurance
            sum = sum / (query.count())
            # That mean value is now updated to the rating field of that specific menu item
            menu_obj.ratings = sum
            menu_obj.save()
            serializer = MenuSerializer(menu_obj)
            response_msg = {"error": False, "message": serializer.data}
        except:
            response_msg = {"error": True, "message": "Something Went Wrong !! "}
        return Response(response_msg)

    def update(self, request, pk=None):
        try:
            # If user has already rated the item
            # Now, here only update of the value will be done
            data = request.data
            query = Rating.objects.get(id=pk)
            user_obj = request.user.profile

            query2 = Rating.objects.filter(Q(id=pk) & Q(customer=user_obj))
            if query2.exists():
                query.ratingScore = data['rating']
                query.save()
                menu_obj = data['menuId']
                query3 = Rating.objects.filter(menuName_id=menu_obj)
                sum = 0
                for i in range(query3.count()):
                    rating = getattr(query3[i], "ratingScore")
                    sum += rating

                sum = sum / (query3.count())
                menu_obj2 = Menu.objects.get(id=data['menuId'])
                menu_obj2.ratings = sum
                menu_obj2.save()
                serializer = MenuSerializer(menu_obj2)
                print(serializer.data)

            else:
                response_msg = {"error": True, "message": "FAILED"}
                return Response(response_msg)
            response_msg = {"error": False, "message": serializer.data}
        except:
            response_msg = {"error": True, "message": "Something Went Wrong"}

        return Response(response_msg)


class OwnRating(views.APIView):
    # API for Rating of a specific item for logged-in user is created here
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        data = request.data
        rating_obj = Rating.objects.filter(Q(customer=request.user.profile) & Q(menuName_id=data['menuId']))
        print(rating_obj)
        if rating_obj.exists():
            serializer = RatingSerializers(rating_obj, many=True)
            return Response(serializer.data)
        else:
            response_msg = {"error": True, "message": "Something Went Wrong !! "}
            return Response(response_msg)


class Orders(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        # Listing all orders of an user
        query = Order.objects.filter(cart__customer=request.user.profile).order_by('-id')
        serializer = OrderSerializers(query, many=True)
        all_data = []
        for order in serializer.data:
            print(order)
            cart_product = CartProduct.objects.filter(cart_id=order['cart']['id'])
            cart_product_serializer = CartProductSerializers(cart_product, many=True)
            order['cartproduct'] = cart_product_serializer.data
            all_data.append(order)
        return Response(all_data)

    def retrieve(self, request, pk=None):
        try:
            # Retrieve an order to see order details
            query = Order.objects.get(id=pk)
            serializers = OrderSerializers(query)
            data = serializers.data
            all_data = []
            cartproduct = CartProduct.objects.filter(cart_id=data['cart']['id'])
            cartproduct_serializer = CartProductSerializers( cartproduct, many=True)
            data["cartproduct"] = cartproduct_serializer.data
            all_data.append(data)
            response_msg = {'error': False, "data": all_data}
        except:
            response_msg = {'error': True, "data": "No Data Found !! "}
        return Response(response_msg)

    def create(self, request):
        try:
            # Ordering from cart
            data = request.data
            cart_id = data['cartId']
            address = data['address']
            email = data['email']
            mobile = data['mobile']
            cart_obj = Cart.objects.get(id=cart_id)

            cart_obj.complete = True
            cart_obj.save()
            Order.objects.create(
                cart=cart_obj,
                address=address,
                mobile=mobile,
                email=email,
                total=cart_obj.total
            )
            cartproduct_obj = CartProduct.objects.filter(cart_id=cart_obj)
            serializer = CartProductSerializers(cartproduct_obj, many=True)

            # Updating the total order value of a Menu Item
            for i in serializer.data:
                current_quantity = i['quantity']
                for j in i['menu']:
                    mymenu = Menu.objects.filter(id=j['id']).first()
                    mymenu.total_sold += current_quantity
                    mymenu.save()
                    print(mymenu)
                    print(current_quantity)
            response_msg = {"error": False, "message": "Order Completed"}
        except:
            response_msg = {"error": True, "message": "Something is wrong ! "}

        return Response(response_msg)

    def destroy(self, request, pk=None):
        try:
            # Deleting that order [Depricated. not implemented on frontend]
            order_obj = Order.objects.get(id=pk)
            cart_obj = Cart.objects.get(id=order_obj.cart.id)
            order_obj.delete()
            cart_obj.delete()
            response_msg = {"error": False, "message": "Order is deleted"}
        except:
            response_msg = {"error": True, "message": "Something is wrong !!"}

        return Response(response_msg)


class NoPaginationItem(views.APIView):
    def get(self, request):
        query = Menu.objects.all().order_by('-id')
        serializer = MenuSerializer(query, many=True)
        return Response(serializer.data)


class CategoryView(views.APIView):
    def get(self, request):
        query = Category.objects.all()
        serializer = CategorySerializers(query, many=True)
        return Response(serializer.data)


class AddItems(views.APIView):
    # Adding Menu Item on Menu Model
    # Authorized to Admin Only
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAdminUser, ]

    def post(self, request):
        data = request.data
        serializer = MenuSerializer(data=data, context={"request": request})

        if serializer.is_valid(raise_exception=True):
            cat_id = data["category"]
            serializer.save()
            menu_obj = Menu.objects.last()
            menu_obj.category = Category.objects.get(id=cat_id)
            menu_obj.save()
            return Response({"error": False, "message": "Menu is Added"})
        return Response({"error": True, "message": "Something is wrong"})


class UpdateMenuItems(views.APIView):
    # Updating Fields of a Menu Item
    # Authorized to Admin Only
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAdminUser, ]

    def post(self, request):
        try:
            data = request.data
            menu_obj = Menu.objects.filter(id=data['menu_id']).first()
            serializer = MenuSerializer(menu_obj, data=data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            menu_obj.category = Category.objects.get(id=data['category'])
            menu_obj.save()
            response_msg = {"error": False, "message": "Menu Item Updated"}
        except:
            response_msg = {"error": True, "message": "Can't Update Menu Item"}
        return Response(response_msg)


class DeleteItem(views.APIView):
    # Deleting an Item from Menu
    # Authorized to Admin Only
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAdminUser, ]

    def post(self, request):
        try:
            data = request.data
            menu_obj = Menu.objects.get(id=data['menu_id'])
            menu_obj.delete()
            response_msg = {"error": False, "message": "Product is deleted"}
        except:
            response_msg = {"error": True, "message": "Something is wrong !!"}
        return Response(response_msg)


class TotalTableValues(views.APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAdminUser, ]

    def get(self, request):
        user = User.objects.all().values().count()
        order = Order.objects.all().values().count()
        paid = Order.objects.filter(payment_complete=True).values().count()
        menu = Menu.objects.all().values().count()

        return Response({
            "user": user,
            "order": order,
            "paid": paid,
            "menu": menu
        })


class OrderStatusView(views.APIView):
    # Making the API for the order status field for a drop down
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAdminUser, ]

    def get(self, request):
        query = OrderStatus.objects.all()
        serializer = OrderStatusSerializers(query, many=True)
        return Response(serializer.data)


class AllOrderView(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAdminUser, ]

    def list(self, request):
        # API for listing Every order of Every customer is made here
        query = Order.objects.all().order_by('-id')
        serializer = OrderSerializers(query, many=True)
        return Response(serializer.data)

    def update(self, request, pk=None):
        # Updating the payment status and order status
        try:
            data = request.data

            if data['indicator'] == 'p':
                query = Order.objects.get(id=pk)
                if data['pay_id'] == '1':
                    query.payment_complete = True
                    query.save()
                elif data['pay_id'] == '2':
                    query.payment_complete = False
                    query.save()

            elif data['indicator'] == 'o':
                query = Order.objects.get(id=pk)
                status = OrderStatus.objects.get(id=data['status_id'])
                query.order_status = status
                query.save()

            response_msg = {"error": False, "message": "Successfully Updated"}
        except:
            response_msg = {"error": True, "message": "Couldn't Update"}
        return Response(response_msg)


class AllCustomerReview(views.APIView):
    # No Authorization
    # API Showing Review of every customer
    def get(self, request):
        try:
            query = Review.objects.all().order_by('-id')
            serializer = ReviewSerializers(query, many=True)
            all_data = []
            for cust in serializer.data:
                user = Profile.objects.get(id=cust['customer']['id'])
                user_serializer = ProfileSerializers(user)
                cust['user'] = user_serializer.data
                all_data.append(cust)

            return Response(all_data)
        except:
            return Response({"error": True, "message": "No Data Available"})


class DeleteReviewAdmin(views.APIView):
    # Deleting any customer Review
    # Authorized to Admin Inly
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAdminUser, ]

    def delete(self, request, pk=None):
        query = Review.objects.get(id=pk)
        print(query)
        query.delete()
        return Response({"error": False, "message": "Your Review Deleted"})


class CustomerReview(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def create(self, request):
        # Adding a new review with ratings for the Feedback
        data = request.data
        user = request.user.profile
        Review.objects.create(
            customer=user,
            comment=data['comment'],
            rating=data['rating'],
            remain_star=5 - data['rating']
        )
        return Response({"error": False, "message": "Your Review Added"})

    def destroy(self, request, pk=None):
        # Deleting own review
        user = request.user.profile
        query = Review.objects.filter(Q(id=pk) & Q(customer=user))

        if query.exists():
            query.delete()
            return Response({"error": False, "message": "Your Review Deleted"})
        else:
            return Response({"error": True, "message": "Something Went Wrong"})


class FilterByCategory(views.APIView):
    # Filter Menu Items as per Menu Category

    def post(self, request):
        data = request.data
        print(data)
        query = Menu.objects.filter(category_id=data['id'])
        serializer = MenuSerializer(query, many=True)
        return Response(serializer.data)


class FilterByPrice(views.APIView):
    # Filter Menu Items as per a price range

    def post(self, request):
        data = request.data
        query = Menu.objects.filter(price__range=[data['start'], data['end']])
        serializer = MenuSerializer(query, many=True)
        return Response(serializer.data)



