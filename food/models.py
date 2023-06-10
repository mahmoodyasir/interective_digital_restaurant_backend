from django.db import models
from authentication.models import *

# Create your models here.


class Category(models.Model):
    title = models.CharField(max_length=199)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title


class OrderStatus(models.Model):
    choice = models.CharField(max_length=199)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.choice


class Menu(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)
    price = models.PositiveIntegerField()
    menuImage = models.ImageField(upload_to='static/images/foods', null=True, blank=True)
    menuImageUrl = models.CharField(max_length=255, null=True, blank=True)
    ingredients = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name