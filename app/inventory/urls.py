from django.urls import path
from .views import ProductView, ProductDetailView, SupplyView

urlpatterns = [
    path('products/', ProductView.as_view(), name='products'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('supplies/', SupplyView.as_view(), name='supplies'),
]