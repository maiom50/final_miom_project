from django.contrib import admin
from .models import Sale, ProductSale

class ProductSaleInline(admin.TabularInline):
    model = ProductSale
    extra = 1
    readonly_fields = ('sale_price', 'created_at', 'updated_at')
    fields = ('product', 'quantity', 'sale_price', 'created_at')

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer_name', 'company', 'sale_date', 'total_amount')
    list_filter = ('company', 'sale_date')
    search_fields = ('buyer_name',)
    readonly_fields = ('total_amount', 'created_at', 'updated_at')
    inlines = [ProductSaleInline]
    date_hierarchy = 'sale_date'

@admin.register(ProductSale)
class ProductSaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'sale', 'product', 'quantity', 'sale_price')
    list_filter = ('sale__company', 'sale')
    search_fields = ('product__name', 'sale__buyer_name')
    readonly_fields = ('created_at', 'updated_at')