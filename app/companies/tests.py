from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from authenticate.models import User, Company
from companies.models import Supplier

class SupplierTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='testpass123')
        self.company = Company.objects.create(owner=self.user, name='Test Company')
        self.client.force_authenticate(user=self.user)

    def test_create_supplier(self):
        url = reverse('suppliers')
        data = {
            'name': 'Test Supplier',
            'inn': '1234567890',
            'contact_info': 'Test contact info'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Supplier.objects.count(), 1)