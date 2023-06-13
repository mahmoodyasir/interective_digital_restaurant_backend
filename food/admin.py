from django.contrib import admin
from .models import *

# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['id']
    list_display = ['id', 'title', 'date']
    list_per_page = 10


class OrderStatusAdmin(admin.ModelAdmin):
    search_fields = ['id']
    list_display = ['id', 'choice', 'date']
    list_per_page = 10


class MenuAdmin(admin.ModelAdmin):
    search_fields = ['id']
    list_display = ['id', 'name', 'category', 'price', 'menuImage', 'menuImageUrl', 'ingredients', 'description', 'date']
    list_per_page = 10


class OrderAdmin(admin.ModelAdmin):
    search_fields = ['id', 'cart']
    list_display = ['id', 'email', 'cart', 'mobile', 'address', 'order_status', 'payment_complete']
    list_per_page = 10


admin.site.register(Category, CategoryAdmin)
admin.site.register(OrderStatus, OrderStatusAdmin)
admin.site.register(Menu, MenuAdmin)
admin.site.register(Cart)
admin.site.register(CartProduct)
admin.site.register(Rating)
admin.site.register(Review)
admin.site.register(Order, OrderAdmin)
