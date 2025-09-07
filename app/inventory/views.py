from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from .models import Product, Supply, SupplyProduct
from .serializers import (
    ProductSerializer,
    SupplySerializer,
    SupplyCreateRequestSerializer,
    SupplyProductSerializer
)
from companies.models import Supplier
from authenticate.permissions import IsCompanyMember
from authenticate.models import Storage


class ProductView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCompanyMember]

    def get(self, request):
        if not hasattr(request.user, 'owned_company'):
            return Response(
                {'detail': 'Компания не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        products = Product.objects.filter(company=request.user.owned_company)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not hasattr(request.user, 'owned_company'):
            return Response(
                {'detail': 'Компания не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            storage_id = request.data.get('storage')
            from apps.companies.models import Storage
            try:
                storage = Storage.objects.get(id=storage_id)
                if storage.company != request.user.owned_company:
                    return Response(
                        {'detail': 'Склад не принадлежит вашей компании'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Storage.DoesNotExist:
                return Response(
                    {'detail': 'Склад не найден'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            product = serializer.save(company=request.user.owned_company, quantity=0)
            return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCompanyMember]

    def get_object(self, pk, user):
        try:
            product = Product.objects.get(pk=pk)
            if hasattr(user, 'owned_company') and product.company == user.owned_company:
                return product
            return None
        except Product.DoesNotExist:
            return None

    def get(self, request, pk):
        product = self.get_object(pk, request.user)
        if not product:
            return Response(
                {'detail': 'Товар не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk):
        product = self.get_object(pk, request.user)
        if not product:
            return Response(
                {'detail': 'Товар не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = self.get_object(pk, request.user)
        if not product:
            return Response(
                {'detail': 'Товар не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        product.delete()
        return Response({'detail': 'Товар удален'}, status=status.HTTP_204_NO_CONTENT)


class SupplyView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCompanyMember]

    def get(self, request):
        if not hasattr(request.user, 'owned_company'):
            return Response(
                {'detail': 'Компания не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        supplies = Supply.objects.filter(company=request.user.owned_company)
        serializer = SupplySerializer(supplies, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def post(self, request):
        if not hasattr(request.user, 'owned_company'):
            return Response(
                {'detail': 'Компания не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SupplyCreateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        try:
            supplier = Supplier.objects.get(id=data['supplier_id'])
            if supplier.company != request.user.owned_company:
                return Response(
                    {'detail': 'Поставщик не принадлежит вашей компании'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Supplier.DoesNotExist:
            return Response(
                {'detail': 'Поставщик не найден'},
                status=status.HTTP_400_BAD_REQUEST
            )

        supply = Supply.objects.create(
            company=request.user.owned_company,
            supplier=supplier,
            delivery_date=data['delivery_date']
        )

        total_amount = 0
        supply_products = []

        for item in data['products']:
            try:
                product = Product.objects.get(id=item['product_id'])
                if product.company != request.user.owned_company:
                    raise Product.DoesNotExist

                supply_product = SupplyProduct(
                    supply=supply,
                    product=product,
                    quantity=item['quantity'],
                    purchase_price=product.purchase_price
                )
                supply_products.append(supply_product)

                product.quantity += item['quantity']
                product.save()

                total_amount += product.purchase_price * item['quantity']

            except Product.DoesNotExist:
                supply.delete()
                return Response(
                    {'detail': f'Товар с ID {item["product_id"]} не найден'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        SupplyProduct.objects.bulk_create(supply_products)

        supply.total_amount = total_amount
        supply.save()

        return Response(SupplySerializer(supply).data, status=status.HTTP_201_CREATED)