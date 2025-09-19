"""
Pytest configuration and fixtures for Retail DevOps tests.
"""

import pytest
import os
import django
from django.conf import settings
from django.test.utils import get_runner

# Set up Django settings for testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_devops.settings')
django.setup()


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Set up test database for the entire test session."""
    with django_db_blocker.unblock():
        from django.core.management import call_command
        call_command('migrate', verbosity=0, interactive=False)


@pytest.fixture
def sample_category():
    """Create a sample category for testing."""
    from core.models import Category
    return Category.objects.create(
        name="Test Category",
        description="Test category for pytest"
    )


@pytest.fixture
def sample_product(sample_category):
    """Create a sample product for testing."""
    from core.models import Product
    from decimal import Decimal
    return Product.objects.create(
        name="Test Product",
        category=sample_category,
        description="Test product for pytest",
        price=Decimal('99.99'),
        stock=50,
        is_active=True
    )


@pytest.fixture
def sample_order():
    """Create a sample order for testing."""
    from core.models import Order
    return Order.objects.create(
        customer_name="Test Customer",
        customer_email="test@example.com",
        customer_phone="1234567890",
        shipping_address="123 Test Street, Test City, TC 12345",
        status='pending'
    )


@pytest.fixture
def sample_order_item(sample_order, sample_product):
    """Create a sample order item for testing."""
    from core.models import OrderItem
    from decimal import Decimal
    return OrderItem.objects.create(
        order=sample_order,
        product=sample_product,
        quantity=2,
        price=Decimal('99.99')
    )


@pytest.fixture
def admin_user():
    """Create an admin user for testing."""
    from django.contrib.auth.models import User
    return User.objects.create_user(
        username='admin',
        email='admin@test.com',
        password='admin123',
        is_staff=True,
        is_superuser=True
    )


@pytest.fixture
def client():
    """Create a test client."""
    from django.test import Client
    return Client()


@pytest.fixture
def authenticated_client(admin_user):
    """Create an authenticated test client."""
    from django.test import Client
    client = Client()
    client.login(username='admin', password='admin123')
    return client


@pytest.fixture
def sample_cart_data(sample_product):
    """Create sample cart data for testing."""
    return {
        'product_id': sample_product.id,
        'quantity': 2
    }


@pytest.fixture
def sample_checkout_data():
    """Create sample checkout data for testing."""
    return {
        'customer_name': 'Test Customer',
        'customer_email': 'test@example.com',
        'customer_phone': '1234567890',
        'shipping_address': '123 Test Street, Test City, TC 12345',
        'notes': 'Test order notes'
    }
