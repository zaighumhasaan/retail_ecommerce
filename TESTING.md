# Testing Guide for Retail DevOps

This document provides comprehensive information about testing the Retail DevOps e-commerce application.

## Test Structure

The project includes multiple types of tests organized as follows:

```
retail_devops/
├── core/
│   ├── tests.py              # Unit tests for models
│   ├── test_views.py         # View and API endpoint tests
│   └── test_integration.py   # Integration tests
├── tests/
│   └── test_e2e.py          # End-to-end tests with Playwright
├── conftest.py              # Pytest configuration and fixtures
├── pytest.ini              # Pytest settings
├── run_tests.py             # Test runner script
└── retail_devops/
    └── test_settings.py     # Test-specific Django settings
```

## Test Types

### 1. Unit Tests (`core/tests.py`)

**Purpose**: Test individual model functionality and business logic.

**Coverage**:
- Category model creation, relationships, and properties
- Product model CRUD operations, stock management, and validation
- Order model calculations and status management
- OrderItem model relationships and constraints
- UserProfile model functionality and user relationships
- Model integration and cascade deletions
- Data validation and constraint testing

**Key Test Classes**:
- `CategoryModelTest`: Tests category creation, product count, ordering
- `ProductModelTest`: Tests product CRUD, stock management, deactivation
- `OrderModelTest`: Tests order creation, calculations, status choices
- `OrderItemModelTest`: Tests order item creation, relationships, constraints
- `UserProfileModelTest`: Tests profile creation, full name property
- `ModelIntegrationTest`: Tests complete workflows and relationships

### 2. View Tests (`core/test_views.py`)

**Purpose**: Test view functions, API endpoints, and user interactions.

**Coverage**:
- Home page display and featured products
- Product listing with filtering, search, and pagination
- Cart management (add, update, remove, clear)
- Checkout process and form validation
- Order confirmation and admin functionality
- AJAX API endpoints for cart operations
- Error handling and edge cases

**Key Test Classes**:
- `HomeViewTest`: Tests homepage loading and content display
- `ProductsViewTest`: Tests product listing, filtering, search, pagination
- `CartViewTest`: Tests cart page display and item management
- `CartAPITest`: Tests AJAX cart operations
- `CheckoutViewTest`: Tests checkout process and validation
- `OrderConfirmationViewTest`: Tests order confirmation display
- `AdminViewTest`: Tests admin interface and order management

### 3. Integration Tests (`core/test_integration.py`)

**Purpose**: Test ORM operations, repository boundaries, and complete workflows.

**Coverage**:
- Database operations and ORM functionality
- API endpoint integration with real data
- Complete order workflow from creation to completion
- Admin interface integration
- Database transactions and rollback scenarios
- Stock management across the application
- Cart persistence and session management

**Key Test Classes**:
- `DatabaseIntegrationTest`: Tests ORM operations and relationships
- `APIEndpointIntegrationTest`: Tests API endpoints with real data
- `AdminIntegrationTest`: Tests admin interface functionality
- `DatabaseTransactionTest`: Tests transaction handling and rollbacks

### 4. End-to-End Tests (`tests/test_e2e.py`)

**Purpose**: Test complete user workflows using Playwright browser automation.

**Coverage**:
- Complete user journey: browse → detail → cart → checkout
- Responsive design testing on different screen sizes
- Error handling and edge cases
- Performance metrics and load times
- Admin order management workflows
- Cross-browser compatibility (Chrome, Firefox, Safari)

**Key Test Methods**:
- `test_homepage_loading`: Tests homepage display and navigation
- `test_product_browsing_flow`: Tests product listing and filtering
- `test_add_to_cart_flow`: Tests cart functionality
- `test_checkout_flow`: Tests complete checkout process
- `test_admin_order_management`: Tests admin order management
- `test_responsive_design`: Tests mobile, tablet, desktop layouts
- `test_error_handling`: Tests error scenarios and validation
- `test_performance_metrics`: Tests page load times and performance

## Running Tests

### Prerequisites

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
python -m playwright install
```

### Test Commands

#### Using the Test Runner Script

```bash
# Run all tests
python run_tests.py

# Run specific test types
python run_tests.py --type unit
python run_tests.py --type integration
python run_tests.py --type e2e
python run_tests.py --type coverage
python run_tests.py --type lint
```

#### Using Pytest Directly

```bash
# Run all tests
pytest

# Run specific test files
pytest core/tests.py
pytest core/test_views.py
pytest core/test_integration.py
pytest tests/test_e2e.py

# Run with coverage
pytest --cov=core --cov-report=html

# Run specific test classes
pytest core/tests.py::CategoryModelTest
pytest core/test_views.py::HomeViewTest

# Run with markers
pytest -m integration
pytest -m e2e
pytest -m unit
```

#### Using Django Test Runner

```bash
# Run Django tests
python manage.py test

# Run specific app tests
python manage.py test core

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## Test Configuration

### Pytest Configuration (`pytest.ini`)

```ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = retail_devops.settings
python_files = tests.py test_*.py *_tests.py
addopts = --tb=short --strict-markers --disable-warnings
markers =
    integration: Integration tests
    e2e: End-to-end tests
    unit: Unit tests
    slow: Slow running tests
```

### Test Settings (`retail_devops/test_settings.py`)

- Uses in-memory SQLite for faster tests
- Disables migrations for speed
- Uses MD5 password hashing for faster authentication
- Disables logging and email sending
- Uses dummy cache backend
- Sets up test-specific media and static file handling

### Fixtures (`conftest.py`)

Provides reusable test fixtures:
- `sample_category`: Creates test category
- `sample_product`: Creates test product
- `sample_order`: Creates test order
- `sample_order_item`: Creates test order item
- `admin_user`: Creates admin user
- `client`: Creates test client
- `authenticated_client`: Creates authenticated test client
- `sample_cart_data`: Creates sample cart data
- `sample_checkout_data`: Creates sample checkout data

## Test Data Management

### Sample Data Creation

The project includes a management command to create sample data:

```bash
python manage.py populate_sample_data
```

This creates:
- 6 categories (Electronics, Clothing, Home & Garden, Sports, Books, Beauty)
- 24 sample products across all categories
- Realistic pricing and stock levels

### Test Data Isolation

Each test class uses `setUp()` methods to create isolated test data, ensuring tests don't interfere with each other.

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        python -m playwright install
    - name: Run tests
      run: python run_tests.py --type all
```

## Performance Testing

### Load Testing

The E2E tests include basic performance metrics:
- Page load time testing
- Response time validation
- Memory usage monitoring

### Database Performance

Integration tests verify:
- Query optimization
- Transaction handling
- Bulk operations
- Index usage

## Debugging Tests

### Verbose Output

```bash
pytest -v
pytest --tb=long
```

### Debug Mode

```bash
pytest --pdb
pytest --pdbcls=IPython.terminal.debugger:Pdb
```

### Test Coverage

```bash
pytest --cov=core --cov-report=html --cov-report=term-missing
```

## Best Practices

### Writing Tests

1. **Test Isolation**: Each test should be independent
2. **Clear Naming**: Use descriptive test method names
3. **Arrange-Act-Assert**: Structure tests clearly
4. **Single Responsibility**: Test one thing per test method
5. **Edge Cases**: Test boundary conditions and error scenarios

### Test Data

1. **Use Factories**: Create test data programmatically
2. **Clean Up**: Ensure tests don't leave side effects
3. **Realistic Data**: Use data that resembles production
4. **Minimal Data**: Use only necessary data for each test

### E2E Tests

1. **Critical Paths**: Focus on main user workflows
2. **Cross-Browser**: Test on multiple browsers
3. **Responsive**: Test on different screen sizes
4. **Performance**: Include performance assertions
5. **Error Handling**: Test error scenarios

## Troubleshooting

### Common Issues

1. **Database Issues**: Ensure test database is properly configured
2. **Static Files**: Check static file serving in tests
3. **Media Files**: Verify media file handling
4. **CSRF Issues**: Check CSRF configuration for API tests
5. **Playwright Issues**: Ensure browsers are installed

### Debug Commands

```bash
# Check test database
python manage.py dbshell

# Run specific failing test
pytest core/tests.py::CategoryModelTest::test_category_creation -v

# Run with debug output
pytest --capture=no -v

# Check test settings
python manage.py shell --settings=retail_devops.test_settings
```

## Contributing

When adding new features:

1. Write unit tests for new models and methods
2. Add view tests for new endpoints
3. Include integration tests for new workflows
4. Add E2E tests for critical user paths
5. Update this documentation

## Resources

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Playwright Documentation](https://playwright.dev/python/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
