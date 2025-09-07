from django.db import models
from authenticate.models import Company, Storage
from companies.models import Supplier

class Product(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Компания'
    )
    storage = models.ForeignKey(
        Storage,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Склад'
    )
    name = models.CharField(max_length=255, verbose_name='Название товара')
    description = models.TextField(verbose_name='Описание', blank=True)
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена закупки'
    )
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена продажи'
    )
    quantity = models.PositiveIntegerField(default=0, verbose_name='Количество')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.quantity} шт."

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

class Supply(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='supplies',
        verbose_name='Компания'
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='supplies',
        verbose_name='Поставщик'
    )
    delivery_date = models.DateTimeField(verbose_name='Дата поставки')
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Общая сумма'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Поставка #{self.id} от {self.supplier.name}"

    class Meta:
        verbose_name = 'Поставка'
        verbose_name_plural = 'Поставки'

class SupplyProduct(models.Model):
    supply = models.ForeignKey(
        Supply,
        on_delete=models.CASCADE,
        related_name='supply_products',
        verbose_name='Поставка'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='supply_products',
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена закупки'
    )

    def __str__(self):
        return f"{self.product.name} - {self.quantity} шт."

    class Meta:
        verbose_name = 'Товар в поставке'
        verbose_name_plural = 'Товары в поставках'
        unique_together = ('supply', 'product')