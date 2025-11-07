from django.urls import path
from .views import (
    MealListCreateView, MealDetailView,
    CategoryListCreateView, CategoryDetailView,
    CartView, AddToCartView, UpdateCartItemView, RemoveFromCartView,
    CreateOrderView, SalesReportView, SalesReportPDFView
)

urlpatterns = [
    # 🍔 Meals & Categories
    path('meals/', MealListCreateView.as_view(), name='meal-list'),
    path('meals/<int:pk>/', MealDetailView.as_view(), name='meal-detail'),
    path('categories/', CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),

    # 🛒 Cart system
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', AddToCartView.as_view(), name='cart-add'),
    path('cart/item/<int:pk>/update/', UpdateCartItemView.as_view(), name='cart-update'),
    path('cart/item/<int:pk>/delete/', RemoveFromCartView.as_view(), name='cart-delete'),

    # 🧾 Orders & Reports
    path('order/create/', CreateOrderView.as_view(), name='order-create'),
    path('reports/sales/', SalesReportView.as_view(), name='sales-report'),
    path('reports/pdf/', SalesReportPDFView.as_view(), name='sales-report-pdf'),
]
