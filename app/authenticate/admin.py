from django.contrib import admin
from .models import User, Company, Storage

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'is_active', 'is_staff', 'is_superuser')
    list_display_links = ('id', 'email')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('email',)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'created_at')
    list_display_links = ('id', 'name')
    list_filter = ('created_at',)
    search_fields = ('name', 'owner__email')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'company', 'capacity', 'created_at')
    list_display_links = ('id', 'name')
    list_filter = ('company', 'created_at')
    search_fields = ('name', 'address', 'company__name')
    readonly_fields = ('created_at', 'updated_at')
