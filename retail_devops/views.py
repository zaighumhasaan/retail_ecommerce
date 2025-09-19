from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from products.models import Product, Category

def home_view(request):
    """Homepage view displaying featured products and categories"""
    featured_products = Product.objects.filter(stock__gt=0)[:8]  # Show up to 8 products in stock
    categories = Category.objects.all()[:6]  # Show up to 6 categories
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'home.html', context)

def profile_view(request):
    user = request.user
    if request.method == "POST":
        user.email = request.POST.get("email", user.email)
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("admin_profile")
    return render(request, "admin/profile.html", {"user": user})
