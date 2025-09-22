from django.urls import path
from .views import ProductView, ProductDetailView, StorageProductView, SupplyView

urlpatterns = [
    path('products/', ProductView.as_view(), name='products'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('storage-products/', StorageProductView.as_view(), name='storage-products'),
    path('supplies/', SupplyView.as_view(), name='supplies'),
]