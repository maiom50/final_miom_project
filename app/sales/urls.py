from django.urls import path
from .views import SalesView

urlpatterns = [
    path('', SalesView.as_view(), name='sales'),
]