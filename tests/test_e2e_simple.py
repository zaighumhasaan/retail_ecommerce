"""
Simplified End-to-End (E2E) smoke tests for Retail DevOps application.
Tests critical flows using Playwright with proper async handling.
"""

import pytest
import asyncio
from playwright.async_api import async_playwright
from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from decimal import Decimal
from asgiref.sync import sync_to_async

from core.models import Category, Product, Order, OrderItem


@pytest.mark.e2e
class SimpleE2ETest(LiveServerTestCase):
    """Simplified E2E smoke tests for critical user flows"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = None
        cls.context = None
        cls.page = None

    @classmethod
    def tearDownClass(cls):
        if cls.browser:
            asyncio.run(cls.browser.close())
        super().tearDownClass()

    async def setUp(self):
        """Set up browser and test data"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        
        # Create test data
        await self.create_test_data()

    async def tearDown(self):
        """Clean up browser resources"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()

    async def create_test_data(self):
        """Create test data for E2E tests"""
        # Create category
        self.category = await sync_to_async(Category.objects.create)(
            name="E2E Test Electronics",
            description="Test category for E2E tests"
        )
        
        # Create product
        self.product = await sync_to_async(Product.objects.create)(
            name="E2E Test Smartphone",
            category=self.category,
            description="High-end smartphone for E2E testing",
            price=Decimal('999.99'),
            stock=50,
            is_active=True
        )
        
        # Create admin user
        self.admin_user = await sync_to_async(User.objects.create_user)(
            username='e2e_admin',
            email='admin@e2e.com',
            password='e2e_admin123',
            is_staff=True,
            is_superuser=True
        )

    async def test_homepage_loading(self):
        """Test that homepage loads correctly"""
        await self.page.goto(f"{self.live_server_url}/")
        
        # Check page title
        title = await self.page.title()
        assert "Retail Store" in title
        
        # Check navigation elements
        await self.page.wait_for_selector("nav.navbar")
        
        # Check that products are displayed
        product_cards = await self.page.query_selector_all(".product-card")
        assert len(product_cards) > 0

    async def test_product_browsing(self):
        """Test product browsing functionality"""
        # Navigate to products page
        await self.page.goto(f"{self.live_server_url}/products/")
        
        # Wait for products to load
        await self.page.wait_for_selector(".product-card")
        
        # Check that our test product is displayed
        product_names = await self.page.evaluate("""
            () => Array.from(document.querySelectorAll('.product-card .card-title'))
                .map(el => el.textContent.trim())
        """)
        
        assert "E2E Test Smartphone" in product_names

    async def test_cart_functionality(self):
        """Test basic cart functionality"""
        # Navigate to products page
        await self.page.goto(f"{self.live_server_url}/products/")
        await self.page.wait_for_selector(".product-card")
        
        # Find and click add to cart button
        add_to_cart_buttons = await self.page.query_selector_all(".btn-add-to-cart")
        assert len(add_to_cart_buttons) > 0
        
        # Click add to cart button
        await add_to_cart_buttons[0].click()
        
        # Wait for success message or cart update
        await self.page.wait_for_timeout(1000)
        
        # Navigate to cart page
        await self.page.goto(f"{self.live_server_url}/cart/")
        
        # Verify product is in cart
        await self.page.wait_for_selector(".cart-item")
        cart_items = await self.page.query_selector_all(".cart-item")
        assert len(cart_items) >= 1

    async def test_checkout_process(self):
        """Test checkout process"""
        # Add product to cart first
        await self.page.goto(f"{self.live_server_url}/products/")
        await self.page.wait_for_selector(".product-card")
        
        add_button = await self.page.query_selector(".btn-add-to-cart")
        await add_button.click()
        await self.page.wait_for_timeout(1000)
        
        # Navigate to checkout
        await self.page.goto(f"{self.live_server_url}/checkout/")
        
        # Fill checkout form
        await self.page.fill("input[name='customer_name']", "E2E Test Customer")
        await self.page.fill("input[name='customer_email']", "e2e@test.com")
        await self.page.fill("input[name='customer_phone']", "1234567890")
        await self.page.fill("textarea[name='shipping_address']", "123 E2E Test Street, Test City, TC 12345")
        await self.page.fill("textarea[name='notes']", "E2E test order")
        
        # Submit checkout form
        submit_button = await self.page.query_selector("button[type='submit']")
        await submit_button.click()
        
        # Wait for redirect to confirmation page
        await self.page.wait_for_url("**/order-confirmation/*")
        
        # Verify order confirmation page
        order_id = await self.page.text_content(".order-id")
        assert order_id is not None

    async def test_admin_access(self):
        """Test admin interface access"""
        # Login as admin
        await self.page.goto(f"{self.live_server_url}/admin/login/")
        await self.page.fill("input[name='username']", "e2e_admin")
        await self.page.fill("input[name='password']", "e2e_admin123")
        await self.page.click("input[type='submit']")
        
        # Wait for admin dashboard
        await self.page.wait_for_url("**/admin/")
        
        # Check that we're on admin dashboard
        title = await self.page.title()
        assert "Django administration" in title

    async def test_responsive_design(self):
        """Test responsive design on different screen sizes"""
        # Test mobile view
        await self.page.set_viewport_size({"width": 375, "height": 667})
        await self.page.goto(f"{self.live_server_url}/")
        
        # Check mobile navigation
        mobile_nav = await self.page.query_selector(".navbar-toggler")
        if mobile_nav:
            await mobile_nav.click()
            await self.page.wait_for_selector(".navbar-collapse")
        
        # Test desktop view
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
        await self.page.goto(f"{self.live_server_url}/")
        
        # Check desktop layout
        await self.page.wait_for_selector(".featured-products")

    async def test_error_handling(self):
        """Test error handling"""
        # Test invalid checkout data
        await self.page.goto(f"{self.live_server_url}/checkout/")
        
        # Submit empty form
        submit_button = await self.page.query_selector("button[type='submit']")
        await submit_button.click()
        
        # Check for validation errors
        await self.page.wait_for_timeout(1000)
        error_elements = await self.page.query_selector_all(".alert-danger, .is-invalid")
        assert len(error_elements) > 0

    async def test_performance_basic(self):
        """Test basic performance metrics"""
        # Test page load time
        start_time = await self.page.evaluate("Date.now()")
        await self.page.goto(f"{self.live_server_url}/")
        await self.page.wait_for_load_state("networkidle")
        end_time = await self.page.evaluate("Date.now()")
        
        load_time = end_time - start_time
        assert load_time < 10000  # Should load within 10 seconds
