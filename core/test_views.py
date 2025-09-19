"""
View tests for Retail DevOps application.
Tests all view functions, API endpoints, and business logic.
"""

import json
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError

from .models import Category, Product, Order, OrderItem, UserProfile


class HomeViewTest(TestCase):
    """Test home page view functionality"""
    
    def setUp(self):
        self.client = Client()
        
        # Create test data
        self.category = Category.objects.create(
            name="Test Electronics",
            description="Test category for home view"
        )
        
        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            description="Test product for home view",
            price=Decimal('99.99'),
            stock=50,
            is_active=True
        )
    
    def test_home_page_loads(self):
        """Test that home page loads successfully"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Retail Store")
    
    def test_home_page_shows_categories(self):
        """Test that home page displays categories"""
        response = self.client.get(reverse('home'))
        self.assertContains(response, self.category.name)
        self.assertContains(response, "1")  # Product count
    
    def test_home_page_shows_featured_products(self):
        """Test that home page displays featured products"""
        response = self.client.get(reverse('home'))
        self.assertContains(response, self.product.name)
    
    def test_home_page_cart_count(self):
        """Test that home page shows cart count"""
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
        
        response = self.client.get(reverse('home'))
        self.assertContains(response, "2")  # Cart count


class ProductsViewTest(TestCase):
    """Test products listing view functionality"""
    
    def setUp(self):
        self.client = Client()
        
        # Create test data
        self.category1 = Category.objects.create(name="Electronics")
        self.category2 = Category.objects.create(name="Clothing")
        
        self.product1 = Product.objects.create(
            name="Smartphone",
            category=self.category1,
            price=Decimal('999.99'),
            stock=10,
            is_active=True
        )
        
        self.product2 = Product.objects.create(
            name="T-Shirt",
            category=self.category2,
            price=Decimal('29.99'),
            stock=50,
            is_active=True
        )
        
        self.inactive_product = Product.objects.create(
            name="Inactive Product",
            category=self.category1,
            price=Decimal('49.99'),
            stock=5,
            is_active=False
        )
    
    def test_products_page_loads(self):
        """Test that products page loads successfully"""
        response = self.client.get(reverse('products'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Products")
    
    def test_products_page_shows_active_products(self):
        """Test that only active products are shown"""
        response = self.client.get(reverse('products'))
        self.assertContains(response, self.product1.name)
        self.assertContains(response, self.product2.name)
        self.assertNotContains(response, self.inactive_product.name)
    
    def test_category_filtering(self):
        """Test category filtering functionality"""
        response = self.client.get(f"{reverse('products')}?category={self.category1.id}")
        self.assertContains(response, self.product1.name)
        self.assertNotContains(response, self.product2.name)
    
    def test_search_functionality(self):
        """Test search functionality"""
        response = self.client.get(f"{reverse('products')}?search=Smartphone")
        self.assertContains(response, self.product1.name)
        self.assertNotContains(response, self.product2.name)
    
    def test_sorting_functionality(self):
        """Test sorting functionality"""
        # Test price sorting
        response = self.client.get(f"{reverse('products')}?sort=price")
        self.assertEqual(response.status_code, 200)
        
        # Test name sorting
        response = self.client.get(f"{reverse('products')}?sort=name")
        self.assertEqual(response.status_code, 200)
    
    def test_pagination(self):
        """Test pagination functionality"""
        # Create more products to test pagination
        for i in range(15):
            Product.objects.create(
                name=f"Product {i}",
                category=self.category1,
                price=Decimal('10.00'),
                stock=10,
                is_active=True
            )
        
        response = self.client.get(reverse('products'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Page 1 of 2")  # Assuming 12 per page


class CartViewTest(TestCase):
    """Test cart view functionality"""
    
    def setUp(self):
        self.client = Client()
        
        # Create test data
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            price=Decimal('50.00'),
            stock=10,
            is_active=True
        )
    
    def test_cart_page_loads(self):
        """Test that cart page loads successfully"""
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Shopping Cart")
    
    def test_empty_cart_display(self):
        """Test empty cart display"""
        response = self.client.get(reverse('cart'))
        self.assertContains(response, "Your cart is empty")
    
    def test_cart_with_items(self):
        """Test cart with items"""
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
        
        response = self.client.get(reverse('cart'))
        self.assertContains(response, self.product.name)
        self.assertContains(response, "2")  # Quantity
        self.assertContains(response, "100.00")  # Total price


class CartAPITest(TestCase):
    """Test cart API endpoints"""
    
    def setUp(self):
        self.client = Client()
        
        # Create test data
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            price=Decimal('50.00'),
            stock=10,
            is_active=True
        )
    
    def test_add_to_cart_success(self):
        """Test successful add to cart"""
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
        self.assertIn('added to cart', response_data['message'])
    
    def test_add_to_cart_insufficient_stock(self):
        """Test add to cart with insufficient stock"""
        data = {
            'product_id': self.product.id,
            'quantity': 15  # More than available stock
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
    
    def test_add_to_cart_invalid_product(self):
        """Test add to cart with invalid product"""
        data = {
            'product_id': 99999,  # Non-existent product
            'quantity': 1
        }
        
        response = self.client.post(
            reverse('add_to_cart'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('Product not found', response_data['message'])
    
    def test_update_cart_success(self):
        """Test successful cart update"""
        # First add item to cart
        data = {
            'product_id': self.product.id,
            'quantity': 2
        }
        self.client.post(
            reverse('add_to_cart'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Then update quantity
        update_data = {
            'product_id': self.product.id,
            'quantity': 3
        }
        
        response = self.client.post(
            reverse('update_cart'),
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
    
    def test_remove_from_cart_success(self):
        """Test successful cart item removal"""
        # First add item to cart
        data = {
            'product_id': self.product.id,
            'quantity': 2
        }
        self.client.post(
            reverse('add_to_cart'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Then remove it
        remove_data = {
            'product_id': self.product.id
        }
        
        response = self.client.post(
            reverse('remove_from_cart'),
            data=json.dumps(remove_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
    
    def test_cart_count_api(self):
        """Test cart count API"""
        # Add items to cart
        data = {
            'product_id': self.product.id,
            'quantity': 3
        }
        self.client.post(
            reverse('add_to_cart'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        response = self.client.get(reverse('cart_count'))
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertEqual(response_data['count'], 3)


class CheckoutViewTest(TestCase):
    """Test checkout view functionality"""
    
    def setUp(self):
        self.client = Client()
        
        # Create test data
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            price=Decimal('50.00'),
            stock=10,
            is_active=True
        )
    
    def test_checkout_page_loads(self):
        """Test that checkout page loads successfully"""
        # Add item to cart first
        data = {
            'product_id': self.product.id,
            'quantity': 2
        }
        self.client.post(
            reverse('add_to_cart'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Checkout")
    
    def test_checkout_empty_cart_redirect(self):
        """Test redirect when cart is empty"""
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 302)  # Redirect to cart
        self.assertRedirects(response, reverse('cart'))
    
    def test_checkout_form_submission_success(self):
        """Test successful checkout form submission"""
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
        
        # Submit checkout form
        checkout_data = {
            'customer_name': 'John Doe',
            'customer_email': 'john@example.com',
            'customer_phone': '1234567890',
            'shipping_address': '123 Main St, City, State 12345',
            'notes': 'Test order'
        }
        
        response = self.client.post(reverse('checkout'), checkout_data)
        self.assertEqual(response.status_code, 302)  # Redirect to confirmation
        
        # Verify order was created
        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.customer_name, 'John Doe')
        self.assertEqual(order.total_amount, Decimal('100.00'))
        
        # Verify stock was reduced
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)  # 10 - 2
    
    def test_checkout_form_validation_errors(self):
        """Test checkout form validation"""
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
        
        # Submit incomplete form
        checkout_data = {
            'customer_name': '',  # Missing required field
            'customer_email': 'invalid-email',  # Invalid email
            'shipping_address': ''  # Missing required field
        }
        
        response = self.client.post(reverse('checkout'), checkout_data)
        self.assertEqual(response.status_code, 200)  # Form with errors
        self.assertContains(response, "Please fill in all required fields")


class OrderConfirmationViewTest(TestCase):
    """Test order confirmation view functionality"""
    
    def setUp(self):
        self.client = Client()
        
        # Create test data
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            price=Decimal('50.00'),
            stock=10,
            is_active=True
        )
        
        self.order = Order.objects.create(
            customer_name="John Doe",
            customer_email="john@example.com",
            shipping_address="123 Main St"
        )
        
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=Decimal('50.00')
        )
    
    def test_order_confirmation_page_loads(self):
        """Test that order confirmation page loads successfully"""
        response = self.client.get(reverse('order_confirmation', args=[self.order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Order Confirmation")
        self.assertContains(response, "John Doe")
    
    def test_order_confirmation_invalid_order(self):
        """Test order confirmation with invalid order ID"""
        response = self.client.get(reverse('order_confirmation', args=[99999]))
        self.assertEqual(response.status_code, 404)


class AdminViewTest(TestCase):
    """Test admin view functionality"""
    
    def setUp(self):
        self.client = Client()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )
        
        # Create test data
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            price=Decimal('50.00'),
            stock=10,
            is_active=True
        )
        
        self.order = Order.objects.create(
            customer_name="Test Customer",
            customer_email="test@example.com",
            shipping_address="123 Test St"
        )
    
    def test_admin_login_required(self):
        """Test that admin views require login"""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_admin_dashboard_access(self):
        """Test admin dashboard access"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
    
    def test_order_status_change_api(self):
        """Test order status change API"""
        self.client.login(username='admin', password='admin123')
        
        data = {
            'order_id': self.order.id,
            'new_status': 'processing'
        }
        
        response = self.client.post(reverse('change_order_status'), data)
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Verify status change
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'processing')
    
    def test_order_status_change_invalid_status(self):
        """Test order status change with invalid status"""
        self.client.login(username='admin', password='admin123')
        
        data = {
            'order_id': self.order.id,
            'new_status': 'invalid_status'
        }
        
        response = self.client.post(reverse('change_order_status'), data)
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('Invalid status', response_data['message'])


class ClearCartViewTest(TestCase):
    """Test clear cart view functionality"""
    
    def setUp(self):
        self.client = Client()
        
        # Create test data
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            price=Decimal('50.00'),
            stock=10,
            is_active=True
        )
    
    def test_clear_cart_success(self):
        """Test successful cart clearing"""
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
        
        # Clear cart
        response = self.client.get(reverse('clear_cart'))
        self.assertEqual(response.status_code, 302)  # Redirect to cart
        
        # Verify cart is empty
        response = self.client.get(reverse('cart'))
        self.assertContains(response, "Your cart is empty")


class GetProductPriceViewTest(TestCase):
    """Test get product price view functionality"""
    
    def setUp(self):
        self.client = Client()
        
        # Create test data
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            price=Decimal('75.50'),
            stock=10,
            is_active=True
        )
    
    def test_get_product_price_success(self):
        """Test successful product price retrieval"""
        response = self.client.get(reverse('get_product_price', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertEqual(response_data['price'], 75.50)
    
    def test_get_product_price_invalid_product(self):
        """Test product price retrieval with invalid product ID"""
        response = self.client.get(reverse('get_product_price', args=[99999]))
        self.assertEqual(response.status_code, 404)
        
        response_data = json.loads(response.content)
        self.assertIn('Product not found', response_data['error'])
