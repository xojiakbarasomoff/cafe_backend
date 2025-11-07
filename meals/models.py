from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# ===== CATEGORY =====
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# ===== MEAL =====
class Meal(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    ingredients = models.TextField()
    availability = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="meals")

    def __str__(self):
        return self.name


# ===== CART =====
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.CharField(max_length=5, default='USD')

    def __str__(self):
        return f"{self.user.username}'s Cart"

    @property
    def items(self):
        return self.cart_items.all()

    @property
    def total_price(self):
        total = sum(item.subtotal for item in self.items)
        return round(total, 2)

    def get_total_with_vat(self, vat_percent=12):
        total = self.total_price
        vat = (vat_percent / 100) * total
        return round(total + vat, 2)


# ===== CART ITEM =====
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return float(self.quantity) * float(self.price_at_time)

    def __str__(self):
        return f"{self.meal.name} x {self.quantity}"


# ===== CURRENCY CACHE =====
class CurrencyRateCache(models.Model):
    base_currency = models.CharField(max_length=5, default="USD")
    target_currency = models.CharField(max_length=5)
    rate = models.DecimalField(max_digits=10, decimal_places=4)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.base_currency} → {self.target_currency}: {self.rate}"


# ===== ORDER =====
class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=5, default="USD")
    country = models.CharField(max_length=50, default="UZB")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - {self.status}"


# ===== ORDER ITEM =====
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return float(self.quantity) * float(self.price)

    def __str__(self):
        return f"{self.meal.name} x {self.quantity}"
