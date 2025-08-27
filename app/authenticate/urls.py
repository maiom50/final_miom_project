from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    CompanyView,
    StorageView,
    StorageDetailView
)

urlpatterns = [
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/login/', UserLoginView.as_view(), name='login'),
    path('company/', CompanyView.as_view(), name='company'),
    path('storages/', StorageView.as_view(), name='storages'),
    path('storages/<int:pk>/', StorageDetailView.as_view(), name='storage-detail'),
]