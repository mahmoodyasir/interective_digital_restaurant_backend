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
        print(data)
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
            query = Rating.objects.all()
            sum = 0
            for i in range(query.count()):
                rating = getattr(query[i], "ratingScore")
                sum += rating

            sum = sum/(query.count())
            menu_obj.ratings = sum
            menu_obj.save()
            response_msg = {"error": False, "message": "Rating Added"}
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
                query3 = Rating.objects.all()
                sum = 0
                for i in range(query3.count()):
                    rating = getattr(query3[i], "ratingScore")
                    sum += rating

                sum = sum / (query3.count())
                menu_obj = Menu.objects.get(id=data['menuId'])
                menu_obj.ratings = sum
                menu_obj.save()

            else:
                response_msg = {"error": True, "message": "FAILED"}
                return Response(response_msg)
            response_msg = {"error": False, "message": "Rating Added"}
        except:
            response_msg = {"error": True, "message": "Something Went Wrong"}

        return Response(response_msg)






