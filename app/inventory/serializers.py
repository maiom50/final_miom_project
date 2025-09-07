from rest_framework import serializers
from .models import Product, Supply, SupplyProduct
from companies.serializers import SupplierSerializer


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('company', 'quantity', 'created_at', 'updated_at')


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

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value)
            if product.company != self.context['request'].user.owned_company:
                raise serializers.ValidationError("Товар не принадлежит вашей компании")
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Товар не найден")


class SupplyCreateRequestSerializer(serializers.Serializer):
    supplier_id = serializers.IntegerField()
    delivery_date = serializers.DateTimeField()
    products = SupplyCreateSerializer(many=True)