from django.urls import path, include
from rest_framework import routers
from .views import *

route = routers.DefaultRouter()
route.register("cart", MyCart, basename="cart")
route.register("putrating", RatingView, basename="putrating")
route.register("orders", Orders, basename="orders")
route.register("allorders", AllOrderView, basename="allorders")
route.register("review", CustomerReview, basename="review")


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
    path('delete_item/', DeleteItem.as_view(), name="delete_item"),
    path('total_values/', TotalTableValues.as_view(), name="total_values"),
    path('order_status/', OrderStatusView.as_view(), name="order_status"),
    path('all_review/', AllCustomerReview.as_view(), name="all_review"),
    path('delete_review_admin/<str:pk>/', DeleteReviewAdmin.as_view(), name="delete_review_admin"),
    path('category_filter/', FilterByCategory.as_view(), name="category_filter"),
    path('price_filter/', FilterByPrice.as_view(), name="price_filter"),

]