"""
Comprehensive test suite for Retail DevOps application.
Includes unit tests, integration tests, and model tests.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from decimal import Decimal
import tempfile
import os

from .models import Category, Product, Order, OrderItem, UserProfile


class CategoryModelTest(TestCase):
    """Test Category model functionality"""
    
    def setUp(self):
        self.category = Category.objects.create(
            name="Test Electronics",
            description="Test category for unit tests"
        )
    
    def test_category_creation(self):
        """Test basic category creation"""
        self.assertEqual(self.category.name, "Test Electronics")
        self.assertEqual(self.category.description, "Test category for unit tests")
        self.assertTrue(self.category.created_at)
        self.assertTrue(self.category.updated_at)
    
    def test_category_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.category), "Test Electronics")
    
    def test_category_product_count_property(self):
        """Test product count property"""
        # Initially no products
        self.assertEqual(self.category.product_count, 0)
        
        # Add a product
        product = Product.objects.create(
            name="Test Product",
            category=self.category,
            price=Decimal('99.99'),
            stock=10
        )
        
        # Check product count
        self.assertEqual(self.category.product_count, 1)
    
    def test_category_verbose_name_plural(self):
        """Test verbose name plural"""
        self.assertEqual(Category._meta.verbose_name_plural, "Categories")
    
    def test_category_ordering(self):
        """Test category ordering"""
        category2 = Category.objects.create(name="A Category")
        category3 = Category.objects.create(name="Z Category")
        
        categories = Category.objects.all()
        self.assertEqual(categories[0], category2)  # A Category
        self.assertEqual(categories[1], self.category)  # Test Electronics
        self.assertEqual(categories[2], category3)  # Z Category


class ProductModelTest(TestCase):
    """Test Product model functionality"""
    
    def setUp(self):
        self.category = Category.objects.create(
            name="Test Category",
            description="Test category"
        )
        
        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            description="Test product description",
            price=Decimal('99.99'),
            stock=50,
            is_active=True
        )
    
    def test_product_creation(self):
        """Test basic product creation"""
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.price, Decimal('99.99'))
        self.assertEqual(self.product.stock, 50)
        self.assertTrue(self.product.is_active)
        self.assertTrue(self.product.created_at)
        self.assertTrue(self.product.updated_at)
    
    def test_product_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.product), "Test Product")
    
    def test_product_ordering(self):
        """Test product ordering by creation date"""
        product2 = Product.objects.create(
            name="Older Product",
            category=self.category,
            price=Decimal('50.00'),
            stock=25
        )
        
        products = Product.objects.all()
        # Newest first due to '-created_at' ordering
        self.assertEqual(products[0], product2)  # product2 is newer
        self.assertEqual(products[1], self.product)  # self.product is older
    
    def test_product_category_relationship(self):
        """Test product-category relationship"""
        self.assertEqual(self.product.category, self.category)
        self.assertIn(self.product, self.category.products.all())
    
    def test_product_deactivation(self):
        """Test product deactivation"""
        self.assertTrue(self.product.is_active)
        
        self.product.is_active = False
        self.product.save()
        
        self.assertFalse(self.product.is_active)
    
    def test_product_stock_management(self):
        """Test stock management"""
        original_stock = self.product.stock
        
        # Reduce stock
        self.product.stock -= 10
        self.product.save()
        
        self.assertEqual(self.product.stock, original_stock - 10)
        
        # Increase stock
        self.product.stock += 5
        self.product.save()
        
        self.assertEqual(self.product.stock, original_stock - 5)


class OrderModelTest(TestCase):
    """Test Order model functionality"""
    
    def setUp(self):
        self.order = Order.objects.create(
            customer_name="John Doe",
            customer_email="john@example.com",
            customer_phone="1234567890",
            shipping_address="123 Main St, City, State 12345",
            status='pending',
            notes="Test order notes"
        )
    
    def test_order_creation(self):
        """Test basic order creation"""
        self.assertEqual(self.order.customer_name, "John Doe")
        self.assertEqual(self.order.customer_email, "john@example.com")
        self.assertEqual(self.order.customer_phone, "1234567890")
        self.assertEqual(self.order.shipping_address, "123 Main St, City, State 12345")
        self.assertEqual(self.order.status, 'pending')
        self.assertEqual(self.order.notes, "Test order notes")
        self.assertTrue(self.order.created_at)
        self.assertTrue(self.order.updated_at)
    
    def test_order_str_representation(self):
        """Test string representation"""
        expected = f"Order #{self.order.id} - John Doe"
        self.assertEqual(str(self.order), expected)
    
    def test_order_status_choices(self):
        """Test order status choices"""
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        self.assertIn('pending', valid_statuses)
        self.assertIn('processing', valid_statuses)
        self.assertIn('shipped', valid_statuses)
        self.assertIn('delivered', valid_statuses)
        self.assertIn('cancelled', valid_statuses)
    
    def test_order_total_amount_property(self):
        """Test total amount calculation"""
        # No items initially
        self.assertEqual(self.order.total_amount, 0)
        
        # Create category and product
        category = Category.objects.create(name="Test Category")
        product = Product.objects.create(
            name="Test Product",
            category=category,
            price=Decimal('50.00'),
            stock=10
        )
        
        # Add order item
        OrderItem.objects.create(
            order=self.order,
            product=product,
            quantity=2,
            price=Decimal('50.00')
        )
        
        # Check total amount
        self.assertEqual(self.order.total_amount, Decimal('100.00'))
    
    def test_order_total_items_property(self):
        """Test total items calculation"""
        # No items initially
        self.assertEqual(self.order.total_items, 0)
        
        # Create category and product
        category = Category.objects.create(name="Test Category")
        product = Product.objects.create(
            name="Test Product",
            category=category,
            price=Decimal('50.00'),
            stock=10
        )
        
        # Add order item
        OrderItem.objects.create(
            order=self.order,
            product=product,
            quantity=3,
            price=Decimal('50.00')
        )
        
        # Check total items
        self.assertEqual(self.order.total_items, 3)
    
    def test_order_ordering(self):
        """Test order ordering by creation date"""
        order2 = Order.objects.create(
            customer_name="Jane Doe",
            customer_email="jane@example.com",
            shipping_address="456 Oak St"
        )
        
        orders = Order.objects.all()
        # Newest first due to '-created_at' ordering
        self.assertEqual(orders[0], order2)
        self.assertEqual(orders[1], self.order)


class OrderItemModelTest(TestCase):
    """Test OrderItem model functionality"""
    
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            price=Decimal('50.00'),
            stock=10
        )
        
        self.order = Order.objects.create(
            customer_name="John Doe",
            customer_email="john@example.com",
            shipping_address="123 Main St"
        )
        
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=Decimal('50.00')
        )
    
    def test_order_item_creation(self):
        """Test basic order item creation"""
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.product, self.product)
        self.assertEqual(self.order_item.quantity, 2)
        self.assertEqual(self.order_item.price, Decimal('50.00'))
    
    def test_order_item_str_representation(self):
        """Test string representation"""
        expected = "Test Product x 2"
        self.assertEqual(str(self.order_item), expected)
    
    def test_order_item_total_price_property(self):
        """Test total price calculation"""
        expected_total = 2 * Decimal('50.00')
        self.assertEqual(self.order_item.total_price, expected_total)
    
    def test_order_item_unique_constraint(self):
        """Test unique constraint on order-product combination"""
        # Try to create another order item with same order and product
        with self.assertRaises(IntegrityError):
            OrderItem.objects.create(
                order=self.order,
                product=self.product,
                quantity=1,
                price=Decimal('50.00')
            )
    
    def test_order_item_relationship(self):
        """Test order-item relationship"""
        self.assertIn(self.order_item, self.order.items.all())
        self.assertEqual(self.order_item.order, self.order)


class UserProfileModelTest(TestCase):
    """Test UserProfile model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.profile = UserProfile.objects.create(
            user=self.user,
            phone='1234567890',
            address='123 Test Street',
            bio='Test user bio'
        )
    
    def test_profile_creation(self):
        """Test basic profile creation"""
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.phone, '1234567890')
        self.assertEqual(self.profile.address, '123 Test Street')
        self.assertEqual(self.profile.bio, 'Test user bio')
        self.assertTrue(self.profile.created_at)
        self.assertTrue(self.profile.updated_at)
    
    def test_profile_str_representation(self):
        """Test string representation"""
        expected = "testuser's Profile"
        self.assertEqual(str(self.profile), expected)
    
    def test_profile_full_name_property(self):
        """Test full name property"""
        # With first and last name
        self.assertEqual(self.profile.full_name, "Test User")
        
        # Without first and last name
        self.user.first_name = ''
        self.user.last_name = ''
        self.user.save()
        self.profile.refresh_from_db()
        
        self.assertEqual(self.profile.full_name, "testuser")
    
    def test_profile_user_relationship(self):
        """Test user-profile relationship"""
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.user.profile, self.profile)
