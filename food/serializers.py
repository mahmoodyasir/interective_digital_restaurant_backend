from rest_framework import serializers
from .models import *


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = "__all__"
        depth = 1


class CartSerializers(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"


class CartProductSerializers(serializers.ModelSerializer):
    class Meta:
        model = CartProduct
        fields = "__all__"
        depth = 2


class RatingSerializers(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = "__all__"
        depth = 1


class ReviewSerializers(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"
        depth = 2


class OrderSerializers(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = "__all__"
        depth = 1


class OrderStatusSerializers(serializers.ModelSerializer):
    # order_status = ChoicesField(choices=Order.ORDER_STATUS)

    class Meta:
        model = OrderStatus
        fields = "__all__"

