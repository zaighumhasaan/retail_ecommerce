from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('cart/', views.cart, name='cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    
    # Health check endpoint
    path('health/', views.health_check, name='health_check'),
    path('debug/', views.debug_info, name='debug_info'),
    
    # AJAX endpoints
    path('api/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('api/update-cart/', views.update_cart, name='update_cart'),
    path('api/remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path('api/cart-count/', views.cart_count, name='cart_count'),
    path('api/product-price/<int:product_id>/', views.get_product_price, name='get_product_price'),
    path('api/change-order-status/', views.change_order_status, name='change_order_status'),
]