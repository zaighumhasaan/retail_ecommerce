# Retail E-commerce Web Application

A comprehensive Django-based e-commerce web application with full shopping cart functionality, checkout process, and order management.

## Features

### 🏠 **Home Page**
- Hero section with call-to-action
- Category showcase with product counts
- Featured products grid
- Responsive design with modern UI

### 🛍️ **Product Catalog**
- Product listing with pagination
- Category filtering
- Search functionality
- Sorting options (name, price, date)
- Product cards with images and details

### 🛒 **Shopping Cart**
- Add/remove products
- Update quantities
- Real-time cart count in navigation
- Persistent cart using sessions
- Stock validation

### 💳 **Checkout Process**
- Customer information form
- Order summary
- Terms and conditions
- Order confirmation page
- Email integration ready

### 📦 **Order Management**
- Order creation and tracking
- Order status management
- Order history
- Stock updates on purchase

## Technology Stack

- **Backend**: Django 5.2.6
- **Database**: SQLite (development)
- **Frontend**: Bootstrap 5.3, Font Awesome
- **JavaScript**: Vanilla JS for AJAX functionality

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd retail_devops
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

4. **Create sample data**
   ```bash
   python manage.py populate_sample_data
   ```

5. **Start development server**
   ```bash
   python manage.py runserver
   ```

6. **Access the application**
   - Open your browser and go to `http://127.0.0.1:8000`
   - Admin panel: `http://127.0.0.1:8000/admin`

## Project Structure

```
retail_devops/
├── core/                    # Main Django app
│   ├── management/          # Management commands
│   ├── migrations/          # Database migrations
│   ├── models.py           # Data models
│   ├── views.py            # View functions
│   └── urls.py             # URL patterns
├── templates/              # HTML templates
│   ├── base.html          # Base template
│   ├── home.html          # Home page
│   ├── products.html      # Product listing
│   ├── cart.html          # Shopping cart
│   ├── checkout.html      # Checkout page
│   └── order_confirmation.html
├── static/                # Static files (CSS, JS, images)
├── media/                 # User uploaded files
└── manage.py             # Django management script
```

## Models

### Product
- Name, description, price, stock
- Category relationship
- Image upload support
- Active/inactive status

### Category
- Name and description
- Product count property

### Order
- Customer information
- Shipping address
- Order status tracking
- Timestamps

### OrderItem
- Product and quantity
- Price at time of purchase
- Order relationship

## Key Features Implementation

### Shopping Cart
- Session-based cart storage
- AJAX-powered add/remove/update
- Real-time cart count updates
- Stock validation

### Checkout Process
- Form validation
- Order creation
- Stock deduction
- Cart clearing
- Order confirmation

### Responsive Design
- Mobile-first approach
- Bootstrap 5 components
- Custom CSS for enhanced styling
- Font Awesome icons

## API Endpoints

- `GET /` - Home page
- `GET /products/` - Product listing
- `GET /cart/` - Shopping cart
- `GET /checkout/` - Checkout page
- `POST /api/add-to-cart/` - Add item to cart (AJAX)
- `POST /api/update-cart/` - Update cart item (AJAX)
- `POST /api/remove-from-cart/` - Remove item from cart (AJAX)
- `GET /api/cart-count/` - Get cart count (AJAX)

## Sample Data

The application includes a management command to populate the database with sample data:

```bash
python manage.py populate_sample_data
```

This creates:
- 6 categories (Electronics, Clothing, Home & Garden, Sports, Books, Beauty)
- 24 sample products across all categories
- Realistic pricing and stock levels

## Development

### Adding New Features
1. Create new models in `core/models.py`
2. Add views in `core/views.py`
3. Update URL patterns in `core/urls.py`
4. Create templates in `templates/`
5. Run migrations: `python manage.py makemigrations && python manage.py migrate`

### Customization
- Modify `templates/base.html` for global styling
- Update `core/views.py` for business logic
- Add new static files in `static/` directory
- Customize models in `core/models.py`

## Production Deployment

For production deployment:

1. Set `DEBUG = False` in settings
2. Configure proper database (PostgreSQL recommended)
3. Set up static file serving
4. Configure media file serving
5. Set up email backend for order confirmations
6. Use environment variables for sensitive settings

## License

This project is open source and available under the MIT License.