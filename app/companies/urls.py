from django.urls import path
from .views import SupplierView, SupplierDetailView, CompanyEmployeeView

urlpatterns = [
    path('suppliers/', SupplierView.as_view(), name='suppliers'),
    path('suppliers/<int:pk>/', SupplierDetailView.as_view(), name='supplier-detail'),
    path('employees/', CompanyEmployeeView.as_view(), name='company-employees'),
    path('employees/<int:user_id>/', CompanyEmployeeView.as_view(), name='company-employee-detail'),
]