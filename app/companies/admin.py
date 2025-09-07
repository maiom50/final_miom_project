from django.contrib import admin
from companies.models import Supplier

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'inn', 'company', 'created_at')
    list_filter = ('company',)
    search_fields = ('name', 'inn', 'contact_info')
    readonly_fields = ('created_at', 'updated_at')