from django.urls import path, include
from rest_framework import routers
from .views import *
from .views import obtain_auth_token

route = routers.DefaultRouter()

urlpatterns = [
    path("", include(route.urls)),
    path('login/', obtain_auth_token),
    path('admin_login/', CustomAuthToken.as_view(), name="admin_login"),
    path('register/', RegisterView.as_view(), name="register"),
    path('admin_register/', AdminRegister.as_view(), name="admin_register"),
    path('user/', UserInfoView.as_view(), name="user"),
    path('admin_profile/', AdminProfileView.as_view(), name="admin_profile"),
    path('all_admin_view/', AdminView.as_view(), name="all_admin_view"),


    path('userdataupdate/', UserDataUpdate.as_view(), name="userdataupdate"),
    path('profile_image_update/', ProfileImageUpdate.as_view(), name="profile_image_update"),
    path('change_password/', ChangePassword.as_view(), name="change_password"),
    path('admin_delete/<str:pk>/', AdminDelete.as_view(), name="admin_delete/<str:pk>"),

]