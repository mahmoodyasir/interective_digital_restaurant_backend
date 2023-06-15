from django.shortcuts import render
from django.urls import reverse
from rest_framework import generics, mixins, viewsets, views, status
from rest_framework.response import Response
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken import views as auth_views
from rest_framework.compat import coreapi, coreschema
from rest_framework.schemas import ManualSchema
from django.conf import settings
from .serializers import MyAuthTokenSerializer
from rest_framework.decorators import api_view
from datetime import *


def general(request):
    return render(request, 'general.html')


class MyAuthToken(auth_views.ObtainAuthToken):
    # Customized Token Based Email Authentication.
    serializer_class = MyAuthTokenSerializer
    if coreapi is not None and coreschema is not None:
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="email",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Email",
                        description="Valid email for authentication",
                    ),
                ),
                coreapi.Field(
                    name="password",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Password",
                        description="Valid password for authentication",
                    ),
                ),
            ],
            encoding="application/json",
        )


obtain_auth_token = MyAuthToken.as_view()


class CustomAuthToken(MyAuthToken):
    # Generating tokens for customized User model
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if user.is_staff:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'error': False,
                'admin_token': token.key,
                'user_id': user.pk,
                'email': user.email,
                "message": True
            })
        else:
            return Response({"error": True, "message": False})


class RegisterView(views.APIView):
    # Registering Regular User
    def post(self, request):
        serializers = UserSerializer(data=request.data)

        if serializers.is_valid():
            serializers.save()
            return Response({"error": False, "message": f"User is created for '{serializers.data['email']}'"})
        return Response({"error": True, "message": "Something is wrong"})


class AdminRegister(views.APIView):
    # Registration of Admin User
    def post(self, request):
        serializers = AdminUserSerializer(data=request.data)

        if serializers.is_valid():
            serializers.save()
            return Response({"error": False, "message": f"Admin User is created for '{serializers.data['email']}'"})
        return Response({"error": True, "message": "Something is wrong"})


class AdminView(views.APIView):
    # API for admin User
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAdminUser, ]

    def get(self, request):
        query = Profile.objects.filter(prouser__is_superuser=True).order_by('-id')
        serializer = ProfileSerializers(query, many=True)
        return Response(serializer.data)


class UserInfoView(views.APIView):
    # API for information of currently logged-In USER
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def get(self, request):
        try:
            query1 = UserInfo.objects.get(user_email=request.user)
            query2 = User.objects.get(email=request.user)
            query3 = Profile.objects.get(prouser=request.user)
            serializer = UserInfoSerializer(query1)
            serializer_data = serializer.data
            all_data = []
            serializer_user = UserSerializer(query2)
            serializer_profile = ProfileSerializers(query3)
            serializer_data["user"] = serializer_user.data
            serializer_data["profile"] = serializer_profile.data
            all_data.append(serializer_data)
            response_msg = {"error": False, "data": all_data}
        except:
            response_msg = {"error": True, "message": "Something is wrong !! Try again....."}
        return Response(response_msg)


class UserDataUpdate(views.APIView):
    # Profile Update API for both User and Admin
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        try:
            user = request.user
            data = request.data
            print(data)
            user_obj = UserInfo.objects.get(user_email=user)
            user_obj.user_firstname = data["firstname"]
            user_obj.user_lastname = data["lastname"]
            user_obj.user_nid = data["nid"]
            user_obj.user_phone = data["phone"]
            user_obj.save()

            response_msg = {"error": False, "message": "User Data is Updated"}
        except:
            # Except block executes if the requested user is an Admin User
            try:
                data = request.data
                admin_obj = AdminUserInfo.objects.get(admin_email=user)
                admin_obj.admin_firstname = data["firstname"]
                admin_obj.admin_lastname = data["lastname"]
                admin_obj.admin_nid = data["nid"]
                admin_obj.admin_phone = data["phone"]
                admin_obj.save()
                response_msg = {"error": False, "message": "Admin Data Updated"}
            except:
                response_msg = {"error": True, "message": "Something is Wrong !! "}
        return Response(response_msg)


class ProfileImageUpdate(views.APIView):
    # Updating User image
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        try:
            user = request.user
            data = request.data
            query = Profile.objects.get(prouser=user)

            serializers = ProfileSerializers(query, data=data, context={"request": request})
            # If required fields are not provided, the it will raise exception
            serializers.is_valid(raise_exception=True)
            serializers.save()
            response_msg = {"error": False, "message": "Profile Image Updated !!"}
        except:
            response_msg = {"error": True, "message": "Profile Image not Update !! Try Again ...."}
        return Response(response_msg)


class ChangePassword(views.APIView):
    # Password Changing for both admin and user if old password is correct
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def post(self, request):
        user = request.user
        if user.check_password(request.data['old_pass']):
            user.set_password(request.data['new_pass'])
            user.save()
            response_msg = {"message": True}
            return Response(response_msg)
        else:
            response_msg = {"message": False}
            return Response(response_msg)


class AdminProfileView(views.APIView):
    # Profile View API for admin
    # Runs when browser token is admin token

    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAdminUser, ]

    def get(self, request):
        try:
            query = AdminUserInfo.objects.get(admin_email=request.user)
            query2 = Profile.objects.get(prouser=request.user)
            serializer = AdminUserInfoSerializer(query)
            serializer_data = serializer.data
            all_data = []
            serializer_user = ProfileSerializers(query2)
            serializer_data["profile_info"] = serializer_user.data
            all_data.append(serializer_data)
            response_msg = {"error": False, "data": all_data}
        except:
            response_msg = {"error": True, "message": "Something is wrong !! Try again....."}
        return Response(response_msg)


class AdminDelete(views.APIView):
    # This deletes an admin user
    # Only a registered admin can delete another admin
    # Also, an admin can not delete own self.
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAdminUser, ]

    def post(self, request, pk):
        try:
            query = User.objects.get(id=pk)
            query.delete()
            response_msg = {"error": False, "message": "Admin User Deleted Successfully"}
        except:
            response_msg = {"error": True, "message": "Admin User Couldn't Delete "}
        return Response(response_msg)