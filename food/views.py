from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, mixins, viewsets, views, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .serializers import *
from django.db.models import Q


class MenuView(generics.GenericAPIView, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Menu.objects.all().order_by('id')
    serializer_class = MenuSerializer
    lookup_field = "id"

    def get(self, request, id=None):
        if id:
            return self.retrieve(request)
        else:
            return self.list(request)


class MyCart(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def list(self, request):
        query = Cart.objects.filter(customer=request.user.profile)
        serializers = CartSerializers(query, many=True)
        all_data = []
        for cart in serializers.data:
            cart_product = CartProduct.objects.filter(cart=cart['id'])
            cart_product_serializer = CartProductSerializers(
                cart_product, many=True)
            cart["cartproduct"] = cart_product_serializer.data
            all_data.append(cart)
        return Response(all_data)


class AddToCart(views.APIView):
    uthentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        menu_id = request.data['id']
        menu_obj = Menu.objects.get(id=menu_id)
        cart_cart = Cart.objects.filter(customer=request.user.profile).filter(complete=False).first()

        try:
            if cart_cart:
                this_menu_in_cart = cart_cart.cartproduct_set.filter(menu=menu_obj)

                if this_menu_in_cart.exists():
                    cart_product_uct = CartProduct.objects.filter(menu=menu_obj).filter(cart__complete=False).first()
                    cart_product_uct.quantity += 1
                    cart_product_uct.subtotal += menu_obj.price
                    cart_product_uct.save()
                    cart_cart.total += menu_obj.price
                    cart_cart.save()
                else:
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
                Cart.objects.create(
                    customer=request.user.profile,
                    total=0,
                    complete=False
                )
                new_cart = Cart.objects.filter(customer=request.user.profile).filter(complete=False).first()
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
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def post(self, request):
        cart_product = CartProduct.objects.get(id=request.data['id'])
        cart_obj = cart_product.cart
        cart_obj.total -= cart_product.subtotal
        cart_obj.save()
        cart_product.delete()

        return Response({"message": "cart Product is deleted"})


class DeleteFullCart(views.APIView):
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
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def list(self, request):
        query = Rating.objects.filter(customer=request.user.profile).order_by('-id')
        serializer = RatingSerializers(query, many=True)
        return Response(serializer.data)

    def create(self, request):
        try:
            data = request.data
            customer_obj = request.user.profile
            rating_score = data['rating']
            menuId = data['menuId']
            menu_obj = Menu.objects.get(id=menuId)
            Rating.objects.create(
                customer=customer_obj,
                ratingScore=rating_score,
                menuName=menu_obj
            )
            query = Rating.objects.filter(menuName=menu_obj)
            sum = 0
            for i in range(query.count()):
                rating = getattr(query[i], "ratingScore")
                sum += rating

            sum = sum / (query.count())
            menu_obj.ratings = sum
            menu_obj.save()
            serializer = MenuSerializer(menu_obj)
            response_msg = {"error": False, "message": serializer.data}
        except:
            response_msg = {"error": True, "message": "Something Went Wrong !! "}
        return Response(response_msg)

    def update(self, request, pk=None):
        try:
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
            order_obj = Order.objects.get(id=pk)
            cart_obj = Cart.objects.get(id=order_obj.cart.id)
            order_obj.delete()
            cart_obj.delete()
            response_msg = {"error": False, "message": "Order is deleted"}
        except:
            response_msg = {"error": True, "message": "Something is wrong !!"}

        return Response(response_msg)
