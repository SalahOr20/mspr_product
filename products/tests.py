from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Product

class ProductAPITestCase(APITestCase):

    def setUp(self):
        # Create sample products for testing
        self.product1 = Product.objects.create(name="Product 1", description="Description 1", price=10.99)
        self.product2 = Product.objects.create(name="Product 2", description="Description 2", price=20.99)

    def test_get_product_list(self):
        # Test GET request for listing products
        url = reverse('product-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # There should be two products

    def test_create_product(self):
        # Test POST request for creating a product
        url = reverse('product-list-create')
        data = {
            'name': 'New Product',
            'description': 'New product description',
            'price': 30.50
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 3)  # 2 initial + 1 new product
        self.assertEqual(Product.objects.last().name, 'New Product')

    def test_get_product_detail(self):
        # Test GET request for retrieving a single product
        url = reverse('product-detail', kwargs={'pk': self.product1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.product1.name)

    def test_update_product(self):
        # Test PUT request for updating a product
        url = reverse('product-detail', kwargs={'pk': self.product1.pk})
        data = {
            'name': 'Updated Product',
            'description': 'Updated description',
            'price': 15.99
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.name, 'Updated Product')

    def test_delete_product(self):
        # Test DELETE request for deleting a product
        url = reverse('product-detail', kwargs={'pk': self.product1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 1)  # One product should be deleted
