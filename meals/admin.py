from django.contrib import admin
from .models import Category, Meal, Cart, CartItem

admin.site.register(Category)
admin.site.register(Meal)
admin.site.register(Cart)
admin.site.register(CartItem)
