from rest_framework import serializers
from .models import Product, StorageProduct, Supply, SupplyProduct
from companies.serializers import SupplierSerializer
from django.utils import timezone

class ProductSerializer(serializers.ModelSerializer):
    total_quantity = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('company', 'created_at', 'updated_at')

class StorageProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    storage_name = serializers.CharField(source='storage.name', read_only=True)

    class Meta:
        model = StorageProduct
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class SupplyProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = SupplyProduct
        fields = ('id', 'product', 'product_name', 'quantity', 'purchase_price')
        read_only_fields = ('purchase_price',)

class SupplySerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    products = SupplyProductSerializer(many=True, read_only=True)

    class Meta:
        model = Supply
        fields = '__all__'
        read_only_fields = ('company', 'total_amount', 'created_at', 'updated_at')

class SupplyCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    storage_id = serializers.IntegerField()

    def validate_product_id(self, value):
        try:
            from inventory.models import Product
            product = Product.objects.get(id=value)
            if product.company != self.context['request'].user.owned_company:
                raise serializers.ValidationError("Товар не принадлежит вашей компании")
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Товар не найден")

    def validate_storage_id(self, value):
        try:
            from authenticate.models import Storage
            storage = Storage.objects.get(id=value)
            if storage.company != self.context['request'].user.owned_company:
                raise serializers.ValidationError("Склад не принадлежит вашей компании")
            return value
        except Storage.DoesNotExist:
            raise serializers.ValidationError("Склад не найден")

class SupplyCreateRequestSerializer(serializers.Serializer):
    supplier_id = serializers.IntegerField()
    delivery_date = serializers.DateTimeField()
    products = SupplyCreateSerializer(many=True)

    def validate_delivery_date(self, value):
        if value > timezone.now():
            raise serializers.ValidationError("Дата поставки не может быть в будущем")
        return value