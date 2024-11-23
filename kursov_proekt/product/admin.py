
from django.contrib import admin
from .models import Category, ProductType, Product

# Registering Category model using the @admin.register decorator
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')  # Fields to display in the list view
    search_fields = ('name',)  # Make name searchable
    list_filter = ('name',)  # Filter by category name

# Registering ProductType model using the @admin.register decorator
@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('category', 'name')  # Fields to display in the list view
    search_fields = ('name',)
    list_filter = ('category',)  # Filter by category

# Registering Product model using the @admin.register decorator
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'category', 'product_type', 'price', 'stock_quantity', 'sku', 'brand', 'created_at', 'is_active'
    )
    list_filter = ('category', 'product_type', 'is_active', 'created_at')
    search_fields = ('name', 'sku', 'brand')
    ordering = ('-created_at',)  # Default ordering by created_at (most recent first)
    list_editable = ('price', 'stock_quantity', 'is_active')  # Allow inline editing of specific fields

    # Optional: Adding a custom field to display discounted price
    def get_discounted_price(self, obj):
        return obj.get_discounted_price()
    get_discounted_price.short_description = 'Discounted Price'

    # Optional: Override save method to handle default image
    def save_model(self, request, obj, form, change):
        if not obj.main_image:
            obj.main_image = 'default_image.jpg'  # Set default image if not uploaded
        super().save_model(request, obj, form, change)
