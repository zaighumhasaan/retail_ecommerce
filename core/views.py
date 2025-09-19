from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json

from .models import Product, Category, Order, OrderItem


def get_cart(request):
    """Get cart from session or create new one"""
    cart = request.session.get('cart', {})
    return cart


def save_cart(request, cart):
    """Save cart to session"""
    request.session['cart'] = cart


def get_cart_items(request):
    """Get cart items with product details"""
    cart = get_cart(request)
    cart_items = []
    cart_total = 0
    cart_count = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            if product.stock >= quantity:
                total_price = product.price * quantity
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'price': product.price,
                    'total_price': total_price
                })
                cart_total += total_price
                cart_count += quantity
        except Product.DoesNotExist:
            # Remove invalid product from cart
            del cart[product_id]
            save_cart(request, cart)
    
    return cart_items, cart_total, cart_count


def home(request):
    """Home page view"""
    categories = Category.objects.all()[:4]  # Show first 4 categories
    
    # Get products with images first, then fill with other products
    products_with_images = Product.objects.filter(is_active=True, stock__gt=0).exclude(image__isnull=True).exclude(image='')[:4]
    other_products = Product.objects.filter(is_active=True, stock__gt=0).exclude(id__in=products_with_images.values_list('id', flat=True)).order_by('-created_at')[:4]
    
    featured_products = list(products_with_images) + list(other_products)
    
    # Get cart count for navigation
    _, _, cart_count = get_cart_items(request)
    
    context = {
        'categories': categories,
        'featured_products': featured_products,
        'cart_count': cart_count,
    }
    return render(request, 'home.html', context)


def products(request):
    """Products listing page"""
    products_list = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    selected_category = None
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        try:
            selected_category = Category.objects.get(id=category_id)
            products_list = products_list.filter(category=selected_category)
        except Category.DoesNotExist:
            pass
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products_list = products_list.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by in ['name', '-name', 'price', '-price', 'created_at', '-created_at']:
        products_list = products_list.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(products_list, 12)  # 12 products per page
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    # Get cart count for navigation
    _, _, cart_count = get_cart_items(request)
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'cart_count': cart_count,
    }
    return render(request, 'products.html', context)


def cart(request):
    """Cart view page"""
    cart_items, cart_total, cart_count = get_cart_items(request)
    
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'cart_count': cart_count,
    }
    return render(request, 'cart.html', context)


@require_http_methods(["POST"])
@csrf_exempt
def add_to_cart(request):
    """Add item to cart (AJAX)"""
    try:
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        quantity = int(data.get('quantity', 1))
        
        if quantity <= 0:
            return JsonResponse({'success': False, 'message': 'Invalid quantity'})
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found'})
        
        if product.stock < quantity:
            return JsonResponse({'success': False, 'message': 'Not enough stock available'})
        
        cart = get_cart(request)
        current_quantity = cart.get(product_id, 0)
        new_quantity = current_quantity + quantity
        
        if new_quantity > product.stock:
            return JsonResponse({'success': False, 'message': f'Only {product.stock} items available in stock'})
        
        cart[product_id] = new_quantity
        save_cart(request, cart)
        
        return JsonResponse({
            'success': True, 
            'message': f'{product.name} added to cart successfully!'
        })
        
    except (ValueError, KeyError, json.JSONDecodeError):
        return JsonResponse({'success': False, 'message': 'Invalid request data'})


@require_http_methods(["POST"])
@csrf_exempt
def update_cart(request):
    """Update cart item quantity (AJAX)"""
    try:
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        quantity = int(data.get('quantity', 1))
        
        if quantity <= 0:
            return JsonResponse({'success': False, 'message': 'Invalid quantity'})
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found'})
        
        if product.stock < quantity:
            return JsonResponse({'success': False, 'message': f'Only {product.stock} items available in stock'})
        
        cart = get_cart(request)
        cart[product_id] = quantity
        save_cart(request, cart)
        
        return JsonResponse({'success': True, 'message': 'Cart updated successfully!'})
        
    except (ValueError, KeyError, json.JSONDecodeError):
        return JsonResponse({'success': False, 'message': 'Invalid request data'})


@require_http_methods(["POST"])
@csrf_exempt
def remove_from_cart(request):
    """Remove item from cart (AJAX)"""
    try:
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        
        cart = get_cart(request)
        if product_id in cart:
            del cart[product_id]
            save_cart(request, cart)
            return JsonResponse({'success': True, 'message': 'Item removed from cart'})
        else:
            return JsonResponse({'success': False, 'message': 'Item not found in cart'})
            
    except (ValueError, KeyError, json.JSONDecodeError):
        return JsonResponse({'success': False, 'message': 'Invalid request data'})


def cart_count(request):
    """Get cart count (AJAX)"""
    _, _, cart_count = get_cart_items(request)
    return JsonResponse({'count': cart_count})


def checkout(request):
    """Checkout page"""
    cart_items, cart_total, cart_count = get_cart_items(request)
    
    if not cart_items:
        messages.warning(request, 'Your cart is empty. Add some products before checking out.')
        return redirect('cart')
    
    if request.method == 'POST':
        # Process the order
        customer_name = request.POST.get('customer_name')
        customer_email = request.POST.get('customer_email')
        customer_phone = request.POST.get('customer_phone', '')
        shipping_address = request.POST.get('shipping_address')
        notes = request.POST.get('notes', '')
        
        if not all([customer_name, customer_email, shipping_address]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'checkout.html', {
                'cart_items': cart_items,
                'cart_total': cart_total,
                'cart_count': cart_count,
            })
        
        # Create order
        order = Order.objects.create(
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            shipping_address=shipping_address,
            notes=notes,
            status='pending'
        )
        
        # Create order items and update stock
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price']
            )
            
            # Update product stock
            item['product'].stock -= item['quantity']
            item['product'].save()
        
        # Clear cart
        request.session['cart'] = {}
        
        messages.success(request, 'Order placed successfully!')
        return redirect('order_confirmation', order_id=order.id)
    
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'cart_count': cart_count,
    }
    return render(request, 'checkout.html', context)


def order_confirmation(request, order_id):
    """Order confirmation page"""
    order = get_object_or_404(Order, id=order_id)
    
    # Get cart count for navigation
    _, _, cart_count = get_cart_items(request)
    
    context = {
        'order': order,
        'cart_count': cart_count,
    }
    return render(request, 'order_confirmation.html', context)


def clear_cart(request):
    """Clear entire cart"""
    request.session['cart'] = {}
    messages.success(request, 'Cart cleared successfully!')
    return redirect('cart')


def get_product_price(request, product_id):
    """Get product price for admin interface"""
    try:
        product = Product.objects.get(id=product_id)
        return JsonResponse({'price': float(product.price)})
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)


@require_http_methods(["POST"])
@csrf_exempt
def change_order_status(request):
    """Change order status via AJAX"""
    try:
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('new_status')
        
        if not order_id or not new_status:
            return JsonResponse({'success': False, 'message': 'Missing order_id or new_status'})
        
        # Validate status
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return JsonResponse({'success': False, 'message': 'Invalid status'})
        
        # Get and update order
        try:
            order = Order.objects.get(id=order_id)
            old_status = order.status
            order.status = new_status
            order.save()
            
            return JsonResponse({
                'success': True, 
                'message': f'Order #{order_id} status changed from {old_status} to {new_status}'
            })
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order not found'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


def health_check(request):
    """Health check endpoint for Render deployment"""
    return JsonResponse({
        'status': 'healthy',
        'message': 'Django application is running',
        'timestamp': timezone.now().isoformat()
    })


def debug_info(request):
    """Debug information for troubleshooting"""
    from django.conf import settings
    import os
    
    return JsonResponse({
        'debug': settings.DEBUG,
        'allowed_hosts': settings.ALLOWED_HOSTS,
        'database_engine': settings.DATABASES['default']['ENGINE'],
        'static_url': settings.STATIC_URL,
        'media_url': settings.MEDIA_URL,
        'environment_vars': {
            'DEBUG': os.environ.get('DEBUG'),
            'ALLOWED_HOSTS': os.environ.get('ALLOWED_HOSTS'),
            'DATABASE_URL': os.environ.get('DATABASE_URL', 'Not set')[:50] + '...' if os.environ.get('DATABASE_URL') else 'Not set'
        }
    })