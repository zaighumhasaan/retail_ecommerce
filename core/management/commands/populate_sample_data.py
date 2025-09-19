from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from core.models import Category, Product
import random


class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create categories
        categories_data = [
            {'name': 'Electronics', 'description': 'Latest electronic gadgets and devices'},
            {'name': 'Clothing', 'description': 'Fashion and apparel for all ages'},
            {'name': 'Home & Garden', 'description': 'Everything for your home and garden'},
            {'name': 'Sports', 'description': 'Sports equipment and fitness gear'},
            {'name': 'Books', 'description': 'Books and educational materials'},
            {'name': 'Beauty', 'description': 'Beauty and personal care products'},
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create products
        products_data = [
            # Electronics
            {'name': 'Smartphone Pro Max', 'category': 'Electronics', 'price': 999.99, 'stock': 50, 'description': 'Latest smartphone with advanced features and premium camera system.'},
            {'name': 'Wireless Headphones', 'category': 'Electronics', 'price': 199.99, 'stock': 100, 'description': 'High-quality wireless headphones with noise cancellation.'},
            {'name': 'Laptop Ultra', 'category': 'Electronics', 'price': 1299.99, 'stock': 25, 'description': 'Powerful laptop for work and gaming with long battery life.'},
            {'name': 'Smart Watch', 'category': 'Electronics', 'price': 299.99, 'stock': 75, 'description': 'Fitness tracking smartwatch with health monitoring features.'},
            
            # Clothing
            {'name': 'Cotton T-Shirt', 'category': 'Clothing', 'price': 24.99, 'stock': 200, 'description': 'Comfortable cotton t-shirt in various colors and sizes.'},
            {'name': 'Denim Jeans', 'category': 'Clothing', 'price': 79.99, 'stock': 150, 'description': 'Classic denim jeans with perfect fit and durability.'},
            {'name': 'Winter Jacket', 'category': 'Clothing', 'price': 149.99, 'stock': 80, 'description': 'Warm winter jacket with water-resistant material.'},
            {'name': 'Running Shoes', 'category': 'Clothing', 'price': 89.99, 'stock': 120, 'description': 'Comfortable running shoes with excellent cushioning.'},
            
            # Home & Garden
            {'name': 'Coffee Maker', 'category': 'Home & Garden', 'price': 89.99, 'stock': 60, 'description': 'Automatic coffee maker for perfect morning brew.'},
            {'name': 'Garden Tools Set', 'category': 'Home & Garden', 'price': 49.99, 'stock': 90, 'description': 'Complete set of garden tools for all your gardening needs.'},
            {'name': 'LED Desk Lamp', 'category': 'Home & Garden', 'price': 39.99, 'stock': 110, 'description': 'Adjustable LED desk lamp with multiple brightness levels.'},
            {'name': 'Plant Pot Set', 'category': 'Home & Garden', 'price': 29.99, 'stock': 200, 'description': 'Set of decorative plant pots for indoor plants.'},
            
            # Sports
            {'name': 'Yoga Mat', 'category': 'Sports', 'price': 34.99, 'stock': 80, 'description': 'Non-slip yoga mat for comfortable workouts.'},
            {'name': 'Dumbbell Set', 'category': 'Sports', 'price': 79.99, 'stock': 40, 'description': 'Adjustable dumbbell set for home fitness.'},
            {'name': 'Basketball', 'category': 'Sports', 'price': 24.99, 'stock': 100, 'description': 'Official size basketball for indoor and outdoor play.'},
            {'name': 'Tennis Racket', 'category': 'Sports', 'price': 89.99, 'stock': 50, 'description': 'Professional tennis racket for all skill levels.'},
            
            # Books
            {'name': 'Programming Guide', 'category': 'Books', 'price': 49.99, 'stock': 75, 'description': 'Comprehensive guide to modern programming languages.'},
            {'name': 'Cookbook Collection', 'category': 'Books', 'price': 29.99, 'stock': 120, 'description': 'Collection of delicious recipes from around the world.'},
            {'name': 'History Book', 'category': 'Books', 'price': 19.99, 'stock': 90, 'description': 'Fascinating journey through world history.'},
            {'name': 'Science Fiction Novel', 'category': 'Books', 'price': 14.99, 'stock': 150, 'description': 'Award-winning science fiction novel.'},
            
            # Beauty
            {'name': 'Skincare Set', 'category': 'Beauty', 'price': 59.99, 'stock': 100, 'description': 'Complete skincare routine set for all skin types.'},
            {'name': 'Makeup Kit', 'category': 'Beauty', 'price': 79.99, 'stock': 80, 'description': 'Professional makeup kit with all essential products.'},
            {'name': 'Hair Care Bundle', 'category': 'Beauty', 'price': 39.99, 'stock': 120, 'description': 'Premium hair care products for healthy hair.'},
            {'name': 'Perfume Collection', 'category': 'Beauty', 'price': 99.99, 'stock': 60, 'description': 'Luxury perfume collection with multiple fragrances.'},
        ]
        
        for product_data in products_data:
            category = next(cat for cat in categories if cat.name == product_data['category'])
            
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'category': category,
                    'description': product_data['description'],
                    'price': product_data['price'],
                    'stock': product_data['stock'],
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f'Created product: {product.name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )
