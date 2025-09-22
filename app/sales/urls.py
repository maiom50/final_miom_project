from django.urls import path
from .views import SalesView, SaleDetailView

urlpatterns = [
    path('', SalesView.as_view(), name='sales'),
    path('<int:pk>/', SaleDetailView.as_view(), name='sale-detail'),
]