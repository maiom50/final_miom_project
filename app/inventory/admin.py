from django.contrib import admin
from inventory.models import Product, Supply, SupplyProduct

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'company', 'storage', 'quantity', 'purchase_price', 'sale_price')
    list_filter = ('company', 'storage')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'supplier', 'delivery_date', 'total_amount')
    list_filter = ('company', 'supplier', 'delivery_date')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(SupplyProduct)
class SupplyProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'supply', 'product', 'quantity', 'purchase_price')
    list_filter = ('supply', 'product')