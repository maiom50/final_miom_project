from rest_framework import serializers
from .models import Sale, ProductSale
from inventory.models import Product
from django.utils import timezone

class ProductSaleSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True)

    class Meta:
        model = ProductSale
        fields = ('id', 'product', 'product_id', 'product_name', 'quantity', 'sale_price', 'created_at')
        read_only_fields = ('sale_price', 'created_at')

class SaleSerializer(serializers.ModelSerializer):
    product_sales = ProductSaleSerializer(many=True, read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = Sale
        fields = '__all__'
        read_only_fields = ('company', 'total_amount', 'created_at', 'updated_at')

class ProductSaleCreateSerializer(serializers.Serializer):
    product = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product(self, value):
        try:
            product = Product.objects.get(id=value)
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Товар не найден")

class SaleCreateSerializer(serializers.Serializer):
    buyer_name = serializers.CharField(max_length=255)
    sale_date = serializers.DateTimeField()
    product_sales = ProductSaleCreateSerializer(many=True)

    def validate_sale_date(self, value):
        if value > timezone.now():
            raise serializers.ValidationError("Дата продажи не может быть в будущем")
        return value

class SaleUpdateSerializer(serializers.ModelSerializer):
    sale_date = serializers.DateTimeField(required=False)

    class Meta:
        model = Sale
        fields = ('buyer_name', 'sale_date')

    def validate_sale_date(self, value):
        if value > timezone.now():
            raise serializers.ValidationError("Дата продажи не может быть в будущем")
        return value