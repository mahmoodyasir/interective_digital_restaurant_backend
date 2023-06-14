from django.urls import path, include
from rest_framework import routers
from .views import *

route = routers.DefaultRouter()
route.register("cart", MyCart, basename="cart")
route.register("putrating", RatingView, basename="putrating")
route.register("orders", Orders, basename="orders")


urlpatterns = [
    path("", include(route.urls)),
    path('menu/', MenuView.as_view(), name="menu"),
    path('menu/<int:id>/', MenuView.as_view(), name="menu"),
    path('addtocart/', AddToCart.as_view(), name="addtocart"),
    path('increasecart/', IncreaseCart.as_view(), name="increasecart"),
    path('decreasecart/', DecreaseCart.as_view(), name="decreasecart"),
    path('deletecartproduct/', DeleteCartProduct.as_view(), name="deletecartproduct"),
    path('deletefullcart/', DeleteFullCart.as_view(), name="deletefullcart"),
    path('checkproduct/', AlreadyAddedProductResponse.as_view(), name="checkproduct"),
    path('ownrating/', OwnRating.as_view(), name="ownrating"),
    path('nopagitem/', NoPaginationItem.as_view(), name="nopagitem"),
    path('category/', CategoryView.as_view(), name="category"),
    path('add_item/', AddItems.as_view(), name="add_item"),
    path('update_item/', UpdateMenuItems.as_view(), name="update_item"),

]