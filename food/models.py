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
    total_sold = models.PositiveIntegerField(default=0)
    ratings = models.CharField(max_length=155, default=0)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    customer = models.ForeignKey(Profile, on_delete=models.CASCADE)
    total = models.PositiveIntegerField()
    complete = models.BooleanField(default=False)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart id=={self.id}==Complete=={self.complete}==Customer=={self.customer}"


class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    menu = models.ManyToManyField(Menu)
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    def __str__(self):
        return f"Cart:{self.cart.id}==>CartProduct:{self.id}==Quantity:{self.quantity}==Customer:{self.cart.customer}"


class Rating(models.Model):
    customer = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True)
    ratingScore = models.PositiveIntegerField()
    menuName = models.ForeignKey(Menu, on_delete=models.CASCADE, null=True)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return f"Id=={self.id}, Customer=={self.customer}, Rating=={self.ratingScore}, Menu=={self.menuName}"


class Review(models.Model):
    customer = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True)
    comment = models.CharField(max_length=255, null=True, blank=True)
    rating = models.PositiveIntegerField(default=0)
    remain_star = models.PositiveIntegerField(default=0)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return f"Id=={self.id}, Customer=={self.customer}, Menu=={self.rating}, Comment=={self.comment}"


class Order(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, unique=False)
    address = models.CharField(max_length=255)
    mobile = models.CharField(max_length=16)
    email = models.CharField(max_length=200)
    total = models.PositiveIntegerField()
    order_status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE, default=6)
    payment_complete = models.BooleanField(default=False)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return f"Order id=={self.id}==Complete=={self.cart.complete}==Customer=={self.cart.customer}"




