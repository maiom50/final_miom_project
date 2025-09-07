from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from authenticate.models import User, Company, Storage
from companies.models import Supplier
from inventory.models import Product

class ProductTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='testpass123')
        self.company = Company.objects.create(owner=self.user, name='Test Company')
        self.storage = Storage.objects.create(
            company=self.company,
            name='Test Storage',
            address='Test Address',
            capacity=100
        )
        self.client.force_authenticate(user=self.user)

    def test_create_product(self):
        url = reverse('products')
        data = {
            'name': 'Test Product',
            'description': 'Test Description',
            'purchase_price': '100.00',
            'sale_price': '150.00',
            'storage': self.storage.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)