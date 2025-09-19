from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from django.forms import TextInput, Textarea, ValidationError, ModelForm
from .models import Category, Product, Order, OrderItem, UserProfile


class OrderItemForm(ModelForm):
    class Meta:
        model = OrderItem
        fields = '__all__'
        widgets = {
            'quantity': TextInput(attrs={'class': 'form-control', 'min': '1'}),
            'price': TextInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.product:
            # Set the current product price as default if not set
            if not self.instance.price:
                self.instance.price = self.instance.product.price
        elif 'product' in self.initial and self.initial['product']:
            # Set price from product when creating new item
            try:
                product = Product.objects.get(id=self.initial['product'])
                self.initial['price'] = product.price
            except Product.DoesNotExist:
                pass

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity', 0)
        price = cleaned_data.get('price', 0)
        product = cleaned_data.get('product')
        
        if quantity and quantity <= 0:
            raise ValidationError("Quantity must be greater than 0.")
        
        if price and price < 0:
            raise ValidationError("Price cannot be negative.")
        
        # Check stock availability if product is selected
        if product and quantity:
            if product.stock < quantity:
                raise ValidationError(f"Not enough stock available. Only {product.stock} items in stock.")
            
        return cleaned_data




class OrderItemInline(admin.TabularInline):
    model = OrderItem
    form = OrderItemForm
    extra = 0
    readonly_fields = ('total_price',)
    fields = ('product', 'quantity', 'price', 'total_price')
    can_delete = True
    min_num = 1
    validate_min = True

    def total_price(self, obj):
        if obj.pk:
            return f"${obj.total_price:.2f}"
        return "-"
    total_price.short_description = "Total"

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'product_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'product_count')
    ordering = ('name',)

    def product_count(self, obj):
        try:
            count = obj.products.count()
            if count > 0:
                return format_html('<span class="badge bg-primary">{}</span>', count)
            return format_html('<span class="badge bg-secondary">0</span>')
        except:
            return format_html('<span class="badge bg-secondary">0</span>')
    product_count.short_description = "Products"
    product_count.admin_order_field = "products__count"

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'class': 'form-control'})},
        models.TextField: {'widget': Textarea(attrs={'class': 'form-control', 'rows': 3})},
    }


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('image_thumbnail', 'name', 'category', 'price', 'stock', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'category__name')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    # change_list_template = 'admin/change_list_simple.html'
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'description', 'is_active')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock')
        }),
        ('Image', {
            'fields': ('image', 'image_preview')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['activate_products', 'deactivate_products', 'delete_selected_products']
    list_display_links = ('name',)

    def image_thumbnail(self, obj):
        if obj.image:
            try:
                return format_html(
                    '<img src="{}" class="rounded" style="max-height:50px;max-width:50px;object-fit:cover;" alt="Product Image" />',
                    obj.image.url
                )
            except Exception as e:
                return format_html('<span class="text-danger">Error: {}</span>', str(e))
        return format_html('<span class="text-muted"><i class="bi bi-image"></i> No Image</span>')
    image_thumbnail.short_description = "Image"
    image_thumbnail.admin_order_field = "name"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" class="img-fluid rounded" style="max-height:200px; max-width:200px;" />',
                obj.image.url
            )
        return "No image uploaded"
    image_preview.short_description = "Image Preview"

    def activate_products(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} products activated successfully.")
    activate_products.short_description = "Activate selected products"

    def deactivate_products(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} products deactivated successfully.")
    deactivate_products.short_description = "Deactivate selected products"

    def delete_selected_products(self, request, queryset):
        from django.db import transaction
        count = queryset.count()
        if count > 0:
            try:
                with transaction.atomic():
                    product_names = list(queryset.values_list('name', flat=True))
                    deleted_count = queryset.delete()[0]
                    if deleted_count > 0:
                        self.message_user(
                            request,
                            f"Successfully deleted {deleted_count} product(s): {', '.join(product_names[:5])}" +
                            (f" and {deleted_count - 5} more..." if deleted_count > 5 else ""),
                            level='SUCCESS'
                        )
            except Exception as e:
                self.message_user(request, f"Error deleting products: {str(e)}", level='ERROR')
        else:
            self.message_user(request, "No products selected for deletion.", level='WARNING')
    delete_selected_products.short_description = "Delete selected products"

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'class': 'form-control'})},
        models.TextField: {'widget': Textarea(attrs={'class': 'form-control', 'rows': 3})},
        models.DecimalField: {'widget': TextInput(attrs={'class': 'form-control'})},
        models.PositiveIntegerField: {'widget': TextInput(attrs={'class': 'form-control'})},
    }


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_email', 'status_display', 'total_amount_display', 'total_items_display', 'created_at')
    list_display_links = None  # Remove clickable links
    list_filter = ('status', 'created_at')
    search_fields = ('customer_name', 'customer_email', 'customer_phone')
    readonly_fields = ('created_at', 'updated_at', 'total_amount_display', 'total_items_display')
    # inlines = [OrderItemInline]  # Disabled since edit is not allowed
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']
    change_list_template = 'admin/core/order/change_list.html'
    
    # Disable edit functionality
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Block access to edit page completely"""
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Order editing is not allowed. Use the status dropdown to change order status.")
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Shipping', {
            'fields': ('shipping_address',)
        }),
        ('Order Details', {
            'fields': ('status', 'notes')
        }),
        ('Summary', {
            'fields': ('total_amount_display', 'total_items_display'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_display(self, obj):
        status_colors = {
            'pending': 'bg-warning',
            'processing': 'bg-info',
            'shipped': 'bg-primary',
            'delivered': 'bg-success',
            'cancelled': 'bg-danger'
        }
        color = status_colors.get(obj.status, 'bg-secondary')
        return format_html('<span class="badge {}">{}</span>', color, obj.get_status_display())
    status_display.short_description = "Status"
    status_display.admin_order_field = "status"

    def total_amount_display(self, obj):
        return format_html('<span class="badge bg-success fs-6">${}</span>', obj.total_amount)
    total_amount_display.short_description = "Total Amount"

    def total_items_display(self, obj):
        return format_html('<span class="badge bg-light text-dark">{}</span>', obj.total_items)
    total_items_display.short_description = "Total Items"

    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f"{updated} orders marked as processing.")
    mark_as_processing.short_description = "Mark selected orders as Processing"

    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f"{updated} orders marked as shipped.")
    mark_as_shipped.short_description = "Mark selected orders as Shipped"

    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f"{updated} orders marked as delivered.")
    mark_as_delivered.short_description = "Mark selected orders as Delivered"

    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f"{updated} orders marked as cancelled.")
    mark_as_cancelled.short_description = "Mark selected orders as Cancelled"




    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'class': 'form-control'})},
        models.EmailField: {'widget': TextInput(attrs={'class': 'form-control'})},
        models.TextField: {'widget': Textarea(attrs={'class': 'form-control', 'rows': 3})},
    }


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'total_price_display')
    list_filter = ('order__status', 'order__created_at')
    search_fields = ('order__customer_name', 'product__name')
    readonly_fields = ('total_price_display',)
    list_editable = ('quantity', 'price')
    form = OrderItemForm

    def total_price_display(self, obj):
        return format_html('<span class="badge bg-success">${}</span>', obj.total_price)
    total_price_display.short_description = "Total Price"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone', 'avatar_thumbnail', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone')
    readonly_fields = ('created_at', 'updated_at', 'avatar_preview', 'full_name')
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'full_name')
        }),
        ('Contact Information', {
            'fields': ('phone', 'address')
        }),
        ('Profile', {
            'fields': ('avatar', 'avatar_preview', 'bio')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = "Full Name"

    def avatar_thumbnail(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" class="rounded-circle" style="max-height:40px;max-width:40px; object-fit: cover;" />',
                obj.avatar.url
            )
        return format_html('<span class="text-muted"><i class="fas fa-user"></i></span>')
    avatar_thumbnail.short_description = "Avatar"

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" class="img-fluid rounded-circle" style="max-height:200px; max-width:200px;" />',
                obj.avatar.url
            )
        return "No avatar uploaded"
    avatar_preview.short_description = "Avatar Preview"

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'class': 'form-control'})},
        models.TextField: {'widget': Textarea(attrs={'class': 'form-control', 'rows': 3})},
    }


# Customize the User admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
