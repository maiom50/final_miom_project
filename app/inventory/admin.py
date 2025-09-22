from django.contrib import admin
from inventory.models import Product, StorageProduct, Supply, SupplyProduct

class StorageProductInline(admin.TabularInline):
    model = StorageProduct
    extra = 1
    fields = ('product', 'quantity')

class SupplyProductInline(admin.TabularInline):
    model = SupplyProduct
    extra = 1
    readonly_fields = ('purchase_price',)
    fields = ('product', 'quantity', 'purchase_price')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'company', 'purchase_price', 'sale_price', 'total_quantity')
    list_filter = ('company',)
    search_fields = ('name', 'description')
    readonly_fields = ('total_quantity', 'created_at', 'updated_at')
    inlines = [StorageProductInline]

@admin.register(StorageProduct)
class StorageProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'storage', 'quantity')
    list_filter = ('storage__company', 'storage')
    search_fields = ('product__name', 'storage__name')

@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'supplier', 'delivery_date', 'total_amount')
    list_filter = ('company', 'supplier', 'delivery_date')
    readonly_fields = ('total_amount', 'created_at', 'updated_at')
    inlines = [SupplyProductInline]

@admin.register(SupplyProduct)
class SupplyProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'supply', 'product', 'quantity', 'purchase_price')
    list_filter = ('supply', 'product')