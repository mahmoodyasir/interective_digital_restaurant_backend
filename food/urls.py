from django.urls import path, include
from rest_framework import routers
from .views import *

route = routers.DefaultRouter()
route.register("cart", MyCart, basename="cart")


urlpatterns = [
    path("", include(route.urls)),
    path('menu/', MenuView.as_view(), name="menu"),
    path('addtocart/', AddToCart.as_view(), name="addtocart"),

]