from django.urls import path, include
from rest_framework import routers
from .views import *

route = routers.DefaultRouter()

urlpatterns = [
    path("", include(route.urls)),
    path('menu/', MenuView.as_view(), name="menu"),

]