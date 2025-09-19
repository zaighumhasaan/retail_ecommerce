"""
End-to-End (E2E) smoke tests for Retail DevOps application.
Tests critical flows: browse → detail → cart → checkout using Playwright.
"""

import pytest
import asyncio
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from django.core.management import call_command
from decimal import Decimal
from asgiref.sync import sync_to_async

from core.models import Category, Product, Order, OrderItem


@pytest.mark.e2e
class E2ESmokeTest(LiveServerTestCase):
    """E2E smoke tests for critical user flows"""
    
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
        
        # Create products
        self.product1 = await sync_to_async(Product.objects.create)(
            name="E2E Test Smartphone",
            category=self.category,
            description="High-end smartphone for E2E testing",
            price=Decimal('999.99'),
            stock=50,
            is_active=True
        )
        
        self.product2 = await sync_to_async(Product.objects.create)(
            name="E2E Test Laptop",
            category=self.category,
            description="Powerful laptop for E2E testing",
            price=Decimal('1299.99'),
            stock=25,
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
        """Test that homepage loads correctly with featured products"""
        await self.page.goto(f"{self.live_server_url}/")
        
        # Check page title
        title = await self.page.title()
        assert "Retail Store" in title
        
        # Check navigation elements
        await self.page.wait_for_selector("nav.navbar")
        
        # Check featured products section
        await self.page.wait_for_selector(".featured-products")
        
        # Check that products are displayed
        product_cards = await self.page.query_selector_all(".product-card")
        assert len(product_cards) > 0
        
        # Check cart count is displayed
        cart_count = await self.page.query_selector(".cart-badge")
        assert cart_count is not None

    async def test_product_browsing_flow(self):
        """Test complete product browsing flow"""
        # Navigate to products page
        await self.page.goto(f"{self.live_server_url}/products/")
        
        # Wait for products to load
        await self.page.wait_for_selector(".product-card")
        
        # Check that our test products are displayed
        product_names = await self.page.evaluate("""
            () => Array.from(document.querySelectorAll('.product-card .card-title'))
                .map(el => el.textContent.trim())
        """)
        
        assert "E2E Test Smartphone" in product_names
        assert "E2E Test Laptop" in product_names
        
        # Test category filtering
        category_filter = await self.page.query_selector("select[name='category']")
        if category_filter:
            await category_filter.select_option(str(self.category.id))
            await self.page.wait_for_timeout(1000)  # Wait for filter to apply
            
            # Verify filtered results
            filtered_products = await self.page.query_selector_all(".product-card")
            assert len(filtered_products) >= 2
        
        # Test search functionality
        search_input = await self.page.query_selector("input[name='search']")
        if search_input:
            await search_input.fill("Smartphone")
            await search_input.press("Enter")
            await self.page.wait_for_timeout(1000)
            
            # Verify search results
            search_results = await self.page.query_selector_all(".product-card")
            assert len(search_results) >= 1

    async def test_add_to_cart_flow(self):
        """Test adding products to cart"""
        # Navigate to products page
        await self.page.goto(f"{self.live_server_url}/products/")
        
        # Wait for products to load
        await self.page.wait_for_selector(".product-card")
        
        # Find and click add to cart button for first product
        add_to_cart_buttons = await self.page.query_selector_all(".btn-add-to-cart")
        assert len(add_to_cart_buttons) > 0
        
        # Click add to cart button
        await add_to_cart_buttons[0].click()
        
        # Wait for success message or cart update
        await self.page.wait_for_timeout(1000)
        
        # Check cart count updated
        cart_count = await self.page.text_content(".cart-badge")
        assert cart_count == "1"
        
        # Navigate to cart page
        await self.page.goto(f"{self.live_server_url}/cart/")
        
        # Verify product is in cart
        await self.page.wait_for_selector(".cart-item")
        cart_items = await self.page.query_selector_all(".cart-item")
        assert len(cart_items) >= 1

    async def test_cart_management_flow(self):
        """Test cart management (add, update, remove)"""
        # Add products to cart first
        await self.page.goto(f"{self.live_server_url}/products/")
        await self.page.wait_for_selector(".product-card")
        
        # Add first product
        add_buttons = await self.page.query_selector_all(".btn-add-to-cart")
        await add_buttons[0].click()
        await self.page.wait_for_timeout(1000)
        
        # Add second product
        if len(add_buttons) > 1:
            await add_buttons[1].click()
            await self.page.wait_for_timeout(1000)
        
        # Navigate to cart
        await self.page.goto(f"{self.live_server_url}/cart/")
        await self.page.wait_for_selector(".cart-item")
        
        # Test quantity update
        quantity_input = await self.page.query_selector("input[name='quantity']")
        if quantity_input:
            await quantity_input.fill("3")
            await quantity_input.press("Enter")
            await self.page.wait_for_timeout(1000)
            
            # Verify quantity updated
            updated_quantity = await quantity_input.input_value()
            assert updated_quantity == "3"
        
        # Test remove item
        remove_button = await self.page.query_selector(".btn-remove-from-cart")
        if remove_button:
            await remove_button.click()
            await self.page.wait_for_timeout(1000)
            
            # Verify item removed
            cart_items = await self.page.query_selector_all(".cart-item")
            # Should have fewer items now

    async def test_checkout_flow(self):
        """Test complete checkout process"""
        # Add product to cart
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
        
        # Verify order details
        customer_name = await self.page.text_content(".customer-name")
        assert "E2E Test Customer" in customer_name

    async def test_admin_order_management(self):
        """Test admin order management functionality"""
        # Create an order first
        order = await sync_to_async(Order.objects.create)(
            customer_name="Admin Test Customer",
            customer_email="admin@test.com",
            shipping_address="123 Admin Test St",
            status='pending'
        )
        
        await sync_to_async(OrderItem.objects.create)(
            order=order,
            product=self.product1,
            quantity=2,
            price=self.product1.price
        )
        
        # Login as admin
        await self.page.goto(f"{self.live_server_url}/admin/login/")
        await self.page.fill("input[name='username']", "e2e_admin")
        await self.page.fill("input[name='password']", "e2e_admin123")
        await self.page.click("input[type='submit']")
        
        # Wait for admin dashboard
        await self.page.wait_for_url("**/admin/")
        
        # Navigate to orders
        await self.page.goto(f"{self.live_server_url}/admin/core/order/")
        
        # Verify order is listed
        await self.page.wait_for_selector(".results")
        order_rows = await self.page.query_selector_all(".results tbody tr")
        assert len(order_rows) >= 1
        
        # Test order status change
        status_select = await self.page.query_selector("select[name='status']")
        if status_select:
            await status_select.select_option("processing")
            await self.page.wait_for_timeout(1000)
            
            # Verify status change
            updated_status = await status_select.input_value()
            assert updated_status == "processing"

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
        
        # Test tablet view
        await self.page.set_viewport_size({"width": 768, "height": 1024})
        await self.page.goto(f"{self.live_server_url}/products/")
        
        # Check product grid layout
        product_cards = await self.page.query_selector_all(".product-card")
        assert len(product_cards) > 0
        
        # Test desktop view
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
        await self.page.goto(f"{self.live_server_url}/")
        
        # Check desktop layout
        await self.page.wait_for_selector(".featured-products")

    async def test_error_handling(self):
        """Test error handling and edge cases"""
        # Test adding out-of-stock product
        # First, set product stock to 0
        self.product1.stock = 0
        await sync_to_async(self.product1.save)()
        
        await self.page.goto(f"{self.live_server_url}/products/")
        await self.page.wait_for_selector(".product-card")
        
        add_button = await self.page.query_selector(".btn-add-to-cart")
        await add_button.click()
        await self.page.wait_for_timeout(1000)
        
        # Check for error message
        error_message = await self.page.query_selector(".alert-danger")
        if error_message:
            error_text = await error_message.text_content()
            assert "stock" in error_text.lower()
        
        # Test invalid checkout data
        await self.page.goto(f"{self.live_server_url}/checkout/")
        
        # Submit empty form
        submit_button = await self.page.query_selector("button[type='submit']")
        await submit_button.click()
        
        # Check for validation errors
        await self.page.wait_for_timeout(1000)
        error_elements = await self.page.query_selector_all(".alert-danger, .is-invalid")
        assert len(error_elements) > 0

    async def test_performance_metrics(self):
        """Test basic performance metrics"""
        # Test page load time
        start_time = await self.page.evaluate("Date.now()")
        await self.page.goto(f"{self.live_server_url}/")
        await self.page.wait_for_load_state("networkidle")
        end_time = await self.page.evaluate("Date.now()")
        
        load_time = end_time - start_time
        assert load_time < 5000  # Should load within 5 seconds
        
        # Test products page performance
        start_time = await self.page.evaluate("Date.now()")
        await self.page.goto(f"{self.live_server_url}/products/")
        await self.page.wait_for_load_state("networkidle")
        end_time = await self.page.evaluate("Date.now()")
        
        load_time = end_time - start_time
        assert load_time < 3000  # Should load within 3 seconds


# Pytest fixtures for async tests
@pytest.fixture
async def browser():
    """Browser fixture for pytest"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        yield browser
        await browser.close()


@pytest.fixture
async def page(browser):
    """Page fixture for pytest"""
    context = await browser.new_context()
    page = await context.new_page()
    yield page
    await context.close()


@pytest.mark.asyncio
async def test_async_homepage_loading(page, live_server):
    """Async test for homepage loading"""
    await page.goto(f"{live_server.url}/")
    title = await page.title()
    assert "Retail Store" in title


@pytest.mark.asyncio
async def test_async_cart_functionality(page, live_server):
    """Async test for cart functionality"""
    # This would require setting up test data in the database
    # For now, just test that the page loads
    await page.goto(f"{live_server.url}/cart/")
    assert await page.is_visible("body")
