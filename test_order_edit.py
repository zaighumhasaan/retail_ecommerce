#!/usr/bin/env python
"""
Test script to verify order editing functionality
Run this with: python manage.py shell < test_order_edit.py
"""

from core.models import Order, OrderItem, Product, Category
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

# Create test data if it doesn't exist
def create_test_data():
    # Create a category
    category, created = Category.objects.get_or_create(
        name="Test Category",
        defaults={'description': 'Test category for order editing'}
    )
    
    # Create a product
    product, created = Product.objects.get_or_create(
        name="Test Product",
        defaults={
            'category': category,
            'description': 'Test product for order editing',
            'price': 10.00,
            'stock': 100,
            'is_active': True
        }
    )
    
    # Create a test order
    order, created = Order.objects.get_or_create(
        customer_name="Test Customer",
        defaults={
            'customer_email': 'test@example.com',
            'customer_phone': '1234567890',
            'shipping_address': '123 Test Street, Test City, TC 12345',
            'status': 'pending'
        }
    )
    
    # Create order item
    order_item, created = OrderItem.objects.get_or_create(
        order=order,
        product=product,
        defaults={
            'quantity': 2,
            'price': 10.00
        }
    )
    
    return order, product, category

def test_order_edit():
    print("Creating test data...")
    order, product, category = create_test_data()
    
    print(f"Created order: {order}")
    print(f"Order items: {order.items.count()}")
    
    # Test updating order
    print("\nTesting order update...")
    order.customer_name = "Updated Customer Name"
    order.status = "processing"
    order.save()
    
    print(f"Updated order: {order}")
    print(f"Status: {order.status}")
    
    # Test updating order item
    print("\nTesting order item update...")
    order_item = order.items.first()
    if order_item:
        order_item.quantity = 5
        order_item.save()
        print(f"Updated order item quantity to: {order_item.quantity}")
    
    print("\nOrder editing test completed successfully!")
    return order

if __name__ == "__main__":
    test_order_edit()
