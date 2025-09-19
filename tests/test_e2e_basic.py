"""
Basic End-to-End (E2E) tests for Retail DevOps application.
Simple tests that verify the application works end-to-end.
"""

import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from decimal import Decimal

from core.models import Category, Product, Order, OrderItem


@pytest.mark.e2e
class BasicE2ETest(TestCase):
    """Basic E2E tests using Django test client"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test data
        self.category = Category.objects.create(
            name="E2E Test Electronics",
            description="Test category for E2E tests"
        )
        
        self.product = Product.objects.create(
            name="E2E Test Smartphone",
            category=self.category,
            description="High-end smartphone for E2E testing",
            price=Decimal('999.99'),
            stock=50,
            is_active=True
        )
        
        self.admin_user = User.objects.create_user(
            username='e2e_admin',
            email='admin@e2e.com',
            password='e2e_admin123',
            is_staff=True,
            is_superuser=True
        )

    def test_homepage_loading(self):
        """Test that homepage loads correctly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Retail Store")
        self.assertContains(response, self.product.name)

    def test_product_browsing(self):
        """Test product browsing functionality"""
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertContains(response, "Products")

    def test_cart_functionality(self):
        """Test basic cart functionality"""
        # Add product to cart
        response = self.client.post('/api/add-to-cart/', 
                                  {'product_id': self.product.id, 'quantity': 2},
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Check cart page
        response = self.client.get('/cart/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    def test_checkout_process(self):
        """Test checkout process"""
        # Add product to cart
        self.client.post('/api/add-to-cart/', 
                        {'product_id': self.product.id, 'quantity': 1},
                        content_type='application/json')
        
        # Get checkout page
        response = self.client.get('/checkout/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Checkout")
        
        # Submit checkout form
        checkout_data = {
            'customer_name': 'E2E Test Customer',
            'customer_email': 'e2e@test.com',
            'customer_phone': '1234567890',
            'shipping_address': '123 E2E Test Street, Test City, TC 12345',
            'notes': 'E2E test order'
        }
        
        response = self.client.post('/checkout/', checkout_data)
        self.assertEqual(response.status_code, 302)  # Redirect to confirmation
        
        # Verify order was created
        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.customer_name, 'E2E Test Customer')

    def test_admin_access(self):
        """Test admin interface access"""
        # Test admin login
        response = self.client.post('/admin/login/', {
            'username': 'e2e_admin',
            'password': 'e2e_admin123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
        
        # Test admin dashboard access
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        # Check for admin content instead of specific text
        self.assertContains(response, "admin")

    def test_order_management(self):
        """Test order management functionality"""
        # Create an order
        order = Order.objects.create(
            customer_name="Admin Test Customer",
            customer_email="admin@test.com",
            shipping_address="123 Admin Test St",
            status='pending'
        )
        
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            price=self.product.price
        )
        
        # Login as admin
        self.client.login(username='e2e_admin', password='e2e_admin123')
        
        # Test order list view
        response = self.client.get('/admin/core/order/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, order.customer_name)

    def test_error_handling(self):
        """Test error handling"""
        # Test invalid product ID
        response = self.client.post('/api/add-to-cart/', 
                                  {'product_id': 99999, 'quantity': 1},
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data['success'])

    def test_stock_validation(self):
        """Test stock validation"""
        # Set product stock to 0
        self.product.stock = 0
        self.product.save()
        
        # Try to add to cart
        response = self.client.post('/api/add-to-cart/', 
                                  {'product_id': self.product.id, 'quantity': 1},
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data['success'])
        self.assertIn('Not enough stock', response_data['message'])

    def test_complete_user_journey(self):
        """Test complete user journey from browsing to checkout"""
        # 1. Browse products
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        
        # 2. Add to cart
        response = self.client.post('/api/add-to-cart/', 
                                  {'product_id': self.product.id, 'quantity': 2},
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # 3. View cart
        response = self.client.get('/cart/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        
        # 4. Checkout
        response = self.client.get('/checkout/')
        self.assertEqual(response.status_code, 200)
        
        # 5. Submit order
        checkout_data = {
            'customer_name': 'Complete Journey Customer',
            'customer_email': 'journey@test.com',
            'customer_phone': '1234567890',
            'shipping_address': '123 Journey Street, Test City, TC 12345',
            'notes': 'Complete journey test'
        }
        
        response = self.client.post('/checkout/', checkout_data)
        self.assertEqual(response.status_code, 302)
        
        # 6. Verify order creation
        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.customer_name, 'Complete Journey Customer')
        self.assertEqual(order.total_items, 2)
        
        # 7. Verify stock reduction
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 48)  # 50 - 2
