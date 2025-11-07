from rest_framework import serializers
from .models import Category, Meal, Cart, CartItem, Order, OrderItem


# ===== CATEGORY =====
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


# ===== MEAL =====
class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = '__all__'


# ===== CART ITEM =====
class CartItemSerializer(serializers.ModelSerializer):
    meal_name = serializers.CharField(source='meal.name', read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'meal', 'meal_name', 'quantity', 'price_at_time', 'subtotal']


# ===== CART =====
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source='cart_items', many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'currency', 'items']


# ===== ORDER ITEM =====
class OrderItemSerializer(serializers.ModelSerializer):
    meal_name = serializers.CharField(source='meal.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'meal_name', 'quantity', 'price', 'subtotal']


# ===== ORDER =====
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'created_at',
            'currency',
            'country',
            'status',
            'total_amount',
            'items'
        ]
