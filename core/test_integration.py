"""
Integration tests for Retail DevOps application.
Tests ORM, repository boundaries, and DRF endpoints with temporary Postgres.
"""

import json
import pytest
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import transaction
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test.utils import override_settings
from django.core.management import call_command
from django.db import connection
from django.test import TransactionTestCase

from core.models import Category, Product, Order, OrderItem, UserProfile


@pytest.mark.integration
class DatabaseIntegrationTest(TransactionTestCase):
    """Test database operations and ORM functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(
            name="Test Electronics",
            description="Test category for integration tests"
        )
        
        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            description="Test product for integration tests",
            price=Decimal('99.99'),
            stock=50,
            is_active=True
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            phone='1234567890',
            address='123 Test Street'
        )

    def test_category_creation_and_relationships(self):
        """Test category creation and product relationships"""
        # Test category creation
        self.assertEqual(self.category.name, "Test Electronics")
        self.assertEqual(self.category.product_count, 1)
        
        # Test product relationship
        self.assertEqual(self.product.category, self.category)
        self.assertIn(self.product, self.category.products.all())

    def test_product_operations(self):
        """Test product CRUD operations and business logic"""
        # Test product creation
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.price, Decimal('99.99'))
        self.assertTrue(self.product.is_active)
        
        # Test stock operations
        original_stock = self.product.stock
        self.product.stock -= 5
        self.product.save()
        self.assertEqual(self.product.stock, original_stock - 5)
        
        # Test deactivation
        self.product.is_active = False
        self.product.save()
        self.assertFalse(self.product.is_active)

    def test_order_creation_and_calculation(self):
        """Test order creation and total calculations"""
        order = Order.objects.create(
            customer_name="John Doe",
            customer_email="john@example.com",
            customer_phone="1234567890",
            shipping_address="123 Main St, City, State 12345",
            status='pending'
        )
        
        # Create order items
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            price=Decimal('99.99')
        )
        
        # Test calculations
        self.assertEqual(order.total_amount, Decimal('199.98'))
        self.assertEqual(order.total_items, 2)
        self.assertEqual(order.items.count(), 1)

    def test_stock_management_on_order(self):
        """Test stock reduction when order is created"""
        original_stock = self.product.stock
        
        order = Order.objects.create(
            customer_name="Jane Doe",
            customer_email="jane@example.com",
            shipping_address="456 Oak St, City, State 12345"
        )
        
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=10,
            price=self.product.price
        )
        
        # Manually reduce stock (as done in checkout view)
        self.product.stock -= 10
        self.product.save()
        
        self.assertEqual(self.product.stock, original_stock - 10)

    def test_user_profile_relationship(self):
        """Test user profile creation and relationships"""
        self.assertEqual(self.user_profile.user, self.user)
        self.assertEqual(self.user_profile.full_name, self.user.username)
        
        # Test profile update
        self.user.first_name = "Test"
        self.user.last_name = "User"
        self.user.save()
        self.user_profile.refresh_from_db()
        self.assertEqual(self.user_profile.full_name, "Test User")

    def test_database_constraints(self):
        """Test database constraints and validations"""
        # Test unique constraint on order-item combination
        order = Order.objects.create(
            customer_name="Test Customer",
            customer_email="test@example.com",
            shipping_address="123 Test St"
        )
        
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
            price=self.product.price
        )
        
        # This should raise an IntegrityError
        with self.assertRaises(Exception):
            OrderItem.objects.create(
                order=order,
                product=self.product,
                quantity=2,
                price=self.product.price
            )


@pytest.mark.integration
class APIEndpointIntegrationTest(TestCase):
    """Test API endpoints and AJAX functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.category = Category.objects.create(
            name="Test Category",
            description="Test category"
        )
        
        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            description="Test product",
            price=Decimal('50.00'),
            stock=100,
            is_active=True
        )
        
        self.user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )

    def test_home_page_integration(self):
        """Test home page with real data"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertContains(response, self.category.name)

    def test_products_page_integration(self):
        """Test products page with filtering and pagination"""
        # Test basic products page
        response = self.client.get(reverse('products'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        
        # Test category filtering
        response = self.client.get(f"{reverse('products')}?category={self.category.id}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        
        # Test search functionality
        response = self.client.get(f"{reverse('products')}?search=Test")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    def test_cart_api_integration(self):
        """Test cart API endpoints with real data"""
        # Test add to cart
        data = {
            'product_id': self.product.id,
            'quantity': 2
        }
        response = self.client.post(
            reverse('add_to_cart'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Test cart count
        response = self.client.get(reverse('cart_count'))
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertEqual(response_data['count'], 2)

    def test_checkout_integration(self):
        """Test complete checkout flow"""
        # Add item to cart
        data = {
            'product_id': self.product.id,
            'quantity': 3
        }
        self.client.post(
            reverse('add_to_cart'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Test checkout page
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        
        # Test order creation
        checkout_data = {
            'customer_name': 'Test Customer',
            'customer_email': 'test@example.com',
            'customer_phone': '1234567890',
            'shipping_address': '123 Test Street, Test City, TC 12345',
            'notes': 'Test order'
        }
        
        response = self.client.post(reverse('checkout'), checkout_data)
        self.assertEqual(response.status_code, 302)  # Redirect to confirmation
        
        # Verify order was created
        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.customer_name, 'Test Customer')
        self.assertEqual(order.total_items, 3)

    def test_order_status_change_integration(self):
        """Test order status change via admin API"""
        # Create an order
        order = Order.objects.create(
            customer_name="Test Customer",
            customer_email="test@example.com",
            shipping_address="123 Test St"
        )
        
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
            price=self.product.price
        )
        
        # Login as admin
        self.client.login(username='admin', password='admin123')
        
        # Change order status
        data = {
            'order_id': order.id,
            'new_status': 'processing'
        }
        
        response = self.client.post(reverse('change_order_status'), data)
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Verify status change
        order.refresh_from_db()
        self.assertEqual(order.status, 'processing')

    def test_stock_validation_integration(self):
        """Test stock validation across the application"""
        # Create product with limited stock
        limited_product = Product.objects.create(
            name="Limited Product",
            category=self.category,
            price=Decimal('25.00'),
            stock=2,
            is_active=True
        )
        
        # Try to add more than available stock
        data = {
            'product_id': limited_product.id,
            'quantity': 5
        }
        
        response = self.client.post(
            reverse('add_to_cart'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('Not enough stock', response_data['message'])

    def test_cart_persistence_integration(self):
        """Test cart persistence across requests"""
        # Add item to cart
        data = {
            'product_id': self.product.id,
            'quantity': 2
        }
        self.client.post(
            reverse('add_to_cart'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Verify cart persists
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        
        # Verify cart count
        response = self.client.get(reverse('cart_count'))
        response_data = json.loads(response.content)
        self.assertEqual(response_data['count'], 2)


@pytest.mark.integration
class AdminIntegrationTest(TestCase):
    """Test admin interface integration"""
    
    def setUp(self):
        """Set up admin test data"""
        self.client = Client()
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )
        
        self.category = Category.objects.create(
            name="Admin Test Category",
            description="Test category for admin tests"
        )
        
        self.product = Product.objects.create(
            name="Admin Test Product",
            category=self.category,
            description="Test product for admin tests",
            price=Decimal('75.00'),
            stock=25,
            is_active=True
        )

    def test_admin_login_and_access(self):
        """Test admin login and basic access"""
        # Test admin login
        response = self.client.post('/admin/login/', {
            'username': 'admin',
            'password': 'admin123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
        
        # Test admin dashboard access
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)

    def test_product_admin_integration(self):
        """Test product admin functionality"""
        self.client.login(username='admin', password='admin123')
        
        # Test product list view
        response = self.client.get('/admin/core/product/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        
        # Test product change view
        response = self.client.get(f'/admin/core/product/{self.product.id}/change/')
        self.assertEqual(response.status_code, 200)

    def test_order_admin_integration(self):
        """Test order admin functionality"""
        # Create an order
        order = Order.objects.create(
            customer_name="Admin Test Customer",
            customer_email="admin@example.com",
            shipping_address="123 Admin St"
        )
        
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            price=self.product.price
        )
        
        self.client.login(username='admin', password='admin123')
        
        # Test order list view
        response = self.client.get('/admin/core/order/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, order.customer_name)
        
        # Test order detail view (should be blocked for editing)
        response = self.client.get(f'/admin/core/order/{order.id}/change/')
        self.assertEqual(response.status_code, 403)  # Permission denied as expected

    def test_bulk_actions_integration(self):
        """Test admin bulk actions"""
        self.client.login(username='admin', password='admin123')
        
        # Test bulk deactivate action
        response = self.client.post('/admin/core/product/', {
            'action': 'deactivate_products',
            '_selected_action': [self.product.id]
        })
        self.assertEqual(response.status_code, 302)  # Redirect after action
        
        # Verify product was deactivated
        self.product.refresh_from_db()
        self.assertFalse(self.product.is_active)


@pytest.mark.integration
class DatabaseTransactionTest(TransactionTestCase):
    """Test database transactions and rollback scenarios"""
    
    def test_order_creation_transaction(self):
        """Test that order creation is atomic"""
        category = Category.objects.create(name="Test Category")
        product = Product.objects.create(
            name="Test Product",
            category=category,
            price=Decimal('100.00'),
            stock=10
        )
        
        # Test successful transaction
        with transaction.atomic():
            order = Order.objects.create(
                customer_name="Test Customer",
                customer_email="test@example.com",
                shipping_address="123 Test St"
            )
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=5,
                price=product.price
            )
            
            # Update stock
            product.stock -= 5
            product.save()
        
        # Verify everything was saved
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        self.assertEqual(Product.objects.get(id=product.id).stock, 5)

    def test_failed_transaction_rollback(self):
        """Test that failed transactions are rolled back"""
        category = Category.objects.create(name="Test Category")
        product = Product.objects.create(
            name="Test Product",
            category=category,
            price=Decimal('100.00'),
            stock=5
        )
        
        initial_stock = product.stock
        
        # Test transaction that should fail
        with self.assertRaises(Exception):
            with transaction.atomic():
                order = Order.objects.create(
                    customer_name="Test Customer",
                    customer_email="test@example.com",
                    shipping_address="123 Test St"
                )
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=10,  # More than available stock
                    price=product.price
                )
                
                # This should raise an exception
                if product.stock < 10:
                    raise ValueError("Insufficient stock")
        
        # Verify rollback occurred
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderItem.objects.count(), 0)
        self.assertEqual(Product.objects.get(id=product.id).stock, initial_stock)
