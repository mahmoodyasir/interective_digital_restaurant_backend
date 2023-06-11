from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, mixins, viewsets, views, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import *


class MenuView(generics.GenericAPIView, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    lookup_field = "id"

    def get(self, request, id=None):
        if id:
            return self.retrieve(request)
        else:
            return self.list(request)

