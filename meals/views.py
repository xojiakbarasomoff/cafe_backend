from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
import requests
from datetime import timedelta
import io

from .models import Meal, Category, Cart, CartItem, Order, OrderItem, CurrencyRateCache
from .serializers import MealSerializer, CategorySerializer, CartSerializer, OrderSerializer

# ===== MEALS =====
class MealListCreateView(generics.ListCreateAPIView):
    queryset = Meal.objects.all()
    serializer_class = MealSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class MealDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Meal.objects.all()
    serializer_class = MealSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# ===== CATEGORY =====
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# ===== CURRENCY CONVERSION =====
def convert_currency(amount, base_currency, target_currency):
    """
    Convert currency using cached rate or fetch new rate from API
    """
    if base_currency == target_currency:
        return round(amount, 2)

    cached = CurrencyRateCache.objects.filter(
        base_currency=base_currency, target_currency=target_currency
    ).first()

    if cached and timezone.now() - cached.last_updated < timedelta(hours=1):
        rate = cached.rate
    else:
        url = f"https://open.er-api.com/v6/latest/{base_currency}"
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            rate = data.get("rates", {}).get(target_currency, 1.0)
        except Exception as e:
            print(f"Currency API error: {e}")
            rate = 1.0

        if cached:
            cached.rate = rate
            cached.save()
        else:
            CurrencyRateCache.objects.create(
                base_currency=base_currency,
                target_currency=target_currency,
                rate=rate
            )

    return round(amount * float(rate), 2)


# ===== CART VIEW =====
class CartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

    def get(self, request, *args, **kwargs):
        cart = self.get_object()
        target_currency = request.GET.get("currency", cart.currency)

        total = cart.total_price
        total_vat = cart.get_total_with_vat()

        converted_total = convert_currency(total, "USD", target_currency)
        converted_total_vat = convert_currency(total_vat, "USD", target_currency)

        return Response({
            "user": request.user.username,
            "currency": target_currency,
            "cart_items": CartSerializer(cart).data["items"],
            "subtotal_usd": total,
            "subtotal_converted": converted_total,
            "total_with_vat": converted_total_vat,
            "vat_percent": 12
        })


# ===== ADD TO CART =====
class AddToCartView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        meal_id = request.data.get("meal_id")
        quantity = int(request.data.get("quantity", 1))

        try:
            meal = Meal.objects.get(id=meal_id)
        except Meal.DoesNotExist:
            return Response({"error": "Meal not found"}, status=status.HTTP_404_NOT_FOUND)

        cart, _ = Cart.objects.get_or_create(user=user)
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            meal=meal,
            defaults={"price_at_time": meal.price, "quantity": quantity}
        )

        if not created:
            item.quantity += quantity
            item.save()

        return Response({
            "message": "Item added to cart",
            "item": {
                "meal": meal.name,
                "quantity": item.quantity,
                "subtotal": item.subtotal
            }
        }, status=status.HTTP_201_CREATED)


# ===== UPDATE CART ITEM =====
class UpdateCartItemView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            item = CartItem.objects.get(id=pk, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

        quantity = request.data.get("quantity")
        if quantity is not None:
            item.quantity = int(quantity)
            item.save()

        return Response({"message": "Item updated", "quantity": item.quantity})


# ===== REMOVE FROM CART =====
class RemoveFromCartView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            item = CartItem.objects.get(id=pk, cart__user=request.user)
            item.delete()
            return Response({"message": "Item removed"}, status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)


# ===== CREATE ORDER =====
class CreateOrderView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(
            user=request.user,
            country=request.data.get("country", "UZB"),
            currency=request.data.get("currency", "USD"),
            total_amount=cart.total_price
        )

        for item in cart.items:
            OrderItem.objects.create(
                order=order,
                meal=item.meal,
                quantity=item.quantity,
                price=item.price_at_time
            )

        cart.items.delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


# ===== SALES REPORT (JSON) =====
class SalesReportView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        monthly_sales = (
            Order.objects.annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(total=Sum("total_amount"))
            .order_by("month")
        )
        regional_sales = (
            Order.objects.values("country")
            .annotate(total=Sum("total_amount"))
            .order_by("-total")
        )
        return Response({
            "monthly_sales": list(monthly_sales),
            "regional_sales": list(regional_sales)
        })


# ===== SALES REPORT PDF EXPORT =====
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class SalesReportPDFView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        monthly_sales = (
            Order.objects.annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(total=Sum("total_amount"))
            .order_by("month")
        )
        regional_sales = (
            Order.objects.values("country")
            .annotate(total=Sum("total_amount"))
            .order_by("-total")
        )

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("Cafe Sales Report", styles["Title"]))
        elements.append(Spacer(1, 12))

        # Monthly Sales
        elements.append(Paragraph("Monthly Sales", styles["Heading2"]))
        monthly_data = [["Month", "Total Sales (USD)"]]
        for item in monthly_sales:
            month_str = item["month"].strftime("%B %Y")
            total = f"${item['total']:,.2f}"
            monthly_data.append([month_str, total])

        monthly_table = Table(monthly_data)
        monthly_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]))
        elements.append(monthly_table)
        elements.append(Spacer(1, 20))

        # Regional Sales
        elements.append(Paragraph("Regional Sales", styles["Heading2"]))
        regional_data = [["Country", "Total Sales (USD)"]]
        for region in regional_sales:
            total = f"${region['total']:,.2f}"
            regional_data.append([region["country"], total])

        regional_table = Table(regional_data)
        regional_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#006633")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]))
        elements.append(regional_table)

        doc.build(elements)
        buffer.seek(0)
        response = HttpResponse(buffer, content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=sales_report.pdf"
        return response
