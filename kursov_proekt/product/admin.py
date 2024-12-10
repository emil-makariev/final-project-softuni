
from django.contrib import admin
from .models import Category, Product

# Registering Category model using the @admin.register decorator
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Fields to display in the list view
    search_fields = ('name',)  # Make name searchable
    list_filter = ('name',)  # Filter by category name



# Registering Product model using the @admin.register decorator

class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'category', 'price', 'sku', 'brand', 'created_at', 'is_active', 'get_max_stock_quantity'
    )
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'sku', 'brand')
    ordering = ('-created_at',)  # Default ordering by created_at (most recent first)
    list_editable = ('price', 'is_active')  # Allow inline editing of specific fields

    # Optional: Adding a custom field to display discounted price
    def get_discounted_price(self, obj):
        return obj.get_discounted_price()
    get_discounted_price.short_description = 'Discounted Price'

    # Optional: Override save method to handle default image
    def save_model(self, request, obj, form, change):
        if not obj.main_image:
            obj.main_image = 'default_image.jpg'  # Set default image if not uploaded
        super().save_model(request, obj, form, change)

    # Display the maximum quantity in the admin interface
    def get_max_stock_quantity(self, obj):
        return obj.get_max_stock_quantity()
    get_max_stock_quantity.short_description = 'Max Stock Quantity'

# Register the Product model with the customized admin interface
admin.site.register(Product, ProductAdmin)
