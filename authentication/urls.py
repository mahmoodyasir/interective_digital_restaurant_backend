from django.urls import path, include
from .views import *
from .views import obtain_auth_token


urlpatterns = [
    path('login/', obtain_auth_token),
    path('admin_login/', CustomAuthToken.as_view(), name="admin_login"),
    path('register/', RegisterView.as_view(), name="register"),
    path('admin_register/', AdminRegister.as_view(), name="admin_register"),
]