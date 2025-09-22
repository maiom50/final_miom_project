from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Sum
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from .models import Sale, ProductSale
from .serializers import (
    SaleSerializer,
    SaleCreateSerializer,
    SaleUpdateSerializer,
    ProductSaleSerializer
)
from inventory.models import Product, StorageProduct
from authenticate.models import Storage
from authenticate.permissions import IsCompanyMember


class SalesView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCompanyMember]

    @extend_schema(
        request=SaleCreateSerializer,
        responses={201: SaleSerializer},
        examples=[
            OpenApiExample(
                'Example',
                value={
                    "buyer_name": "Миомант Миомов",
                    "sale_date": "2025-09-26T10:30:00Z",
                    "product_sales": [
                        {
                            "product": 10,
                            "quantity": 150
                        },
                        {
                            "product": 1,
                            "quantity": 8
                        }
                    ]
                }
            )
        ]
    )
    @transaction.atomic
    def post(self, request):
        if not hasattr(request.user, 'owned_company'):
            return Response(
                {'detail': 'Компания не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            serializer = SaleCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            data = serializer.validated_data

            sale = Sale.objects.create(
                company=request.user.owned_company,
                buyer_name=data['buyer_name'],
                sale_date=data['sale_date']
            )

            total_amount = 0
            product_sales = []

            for item in data['product_sales']:
                try:
                    product = Product.objects.get(id=item['product'])

                    if product.company != request.user.owned_company:
                        sale.delete()
                        return Response(
                            {'detail': f'Товар с ID {item["product"]} не принадлежит вашей компании'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    storage_products = StorageProduct.objects.filter(
                        product=product,
                        storage__company=request.user.owned_company
                    )
                    total_available = storage_products.aggregate(total=Sum('quantity'))['total'] or 0

                    if total_available < item['quantity']:
                        sale.delete()
                        return Response(
                            {
                                'detail': f'Недостаточно товара "{product.name}". Доступно: {total_available}, запрошено: {item["quantity"]}'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    remaining_quantity = item['quantity']
                    for storage_product in storage_products.order_by('id'):
                        if remaining_quantity <= 0:
                            break

                        deduct_quantity = min(remaining_quantity, storage_product.quantity)
                        storage_product.quantity -= deduct_quantity
                        storage_product.save()
                        remaining_quantity -= deduct_quantity

                    product_sale = ProductSale(
                        sale=sale,
                        product=product,
                        quantity=item['quantity'],
                        sale_price=product.sale_price
                    )
                    product_sales.append(product_sale)

                    total_amount += product.sale_price * item['quantity']

                except Product.DoesNotExist:
                    sale.delete()
                    return Response(
                        {'detail': f'Товар с ID {item["product"]} не найден'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            ProductSale.objects.bulk_create(product_sales)

            sale.total_amount = total_amount
            sale.save()

            return Response(SaleSerializer(sale).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'detail': f'Ошибка при создании продажи: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        parameters=[
            OpenApiParameter(name='page', description='Номер страницы', type=int),
            OpenApiParameter(name='page_size', description='Размер страницы', type=int),
            OpenApiParameter(name='start_date', description='Начальная дата (YYYY-MM-DD)', type=str),
            OpenApiParameter(name='end_date', description='Конечная дата (YYYY-MM-DD)', type=str),
        ],
        responses={200: SaleSerializer(many=True)}
    )
    def get(self, request):
        if not hasattr(request.user, 'owned_company'):
            return Response(
                {'detail': 'Компания не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            sales = Sale.objects.filter(company=request.user.owned_company).order_by('-sale_date')

            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')

            if start_date:
                sales = sales.filter(sale_date__date__gte=start_date)

            if end_date:
                sales = sales.filter(sale_date__date__lte=end_date)

            # Пагинация
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))

            paginator = Paginator(sales, page_size)
            page_obj = paginator.get_page(page)

            serializer = SaleSerializer(page_obj, many=True)

            return Response({
                'count': paginator.count,
                'total_pages': paginator.num_pages,
                'current_page': page,
                'results': serializer.data
            })

        except Exception as e:
            return Response(
                {'detail': f'Ошибка при получении продаж: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class SaleDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCompanyMember]

    def get_object(self, pk, user):
        try:
            sale = Sale.objects.get(pk=pk)
            if hasattr(user, 'owned_company') and sale.company == user.owned_company:
                return sale
            return None
        except Sale.DoesNotExist:
            return None

    @extend_schema(responses={200: SaleSerializer})
    def get(self, request, pk):
        sale = self.get_object(pk, request.user)
        if not sale:
            return Response(
                {'detail': 'Продажа не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = SaleSerializer(sale)
        return Response(serializer.data)

    @extend_schema(
        request=SaleUpdateSerializer,
        responses={200: SaleSerializer}
    )
    def put(self, request, pk):
        sale = self.get_object(pk, request.user)
        if not sale:
            return Response(
                {'detail': 'Продажа не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SaleUpdateSerializer(sale, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(SaleSerializer(sale).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def delete(self, request, pk):
        sale = self.get_object(pk, request.user)
        if not sale:
            return Response(
                {'detail': 'Продажа не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        for product_sale in sale.product_sales.all():
            product = product_sale.product

            main_storage = Storage.objects.filter(company=request.user.owned_company).first()
            if main_storage:
                storage_product, created = StorageProduct.objects.get_or_create(
                    storage=main_storage,
                    product=product,
                    defaults={'quantity': 0}
                )
                storage_product.quantity += product_sale.quantity
                storage_product.save()

        sale.delete()

        return Response(
            {'detail': 'Продажа удалена, товары возвращены на склад'},
            status=status.HTTP_204_NO_CONTENT
        )