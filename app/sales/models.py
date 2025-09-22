from django.db import models
from authenticate.models import Company
from inventory.models import Product

class Sale(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='sales',
        verbose_name='Компания'
    )
    buyer_name = models.CharField(max_length=255, verbose_name='Имя покупателя')
    sale_date = models.DateTimeField(verbose_name='Дата продажи')
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Общая сумма'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Продажа #{self.id} - {self.buyer_name}"

    class Meta:
        verbose_name = 'Продажа'
        verbose_name_plural = 'Продажи'
        ordering = ['-sale_date']

class ProductSale(models.Model):
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='product_sales',
        verbose_name='Продажа'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_sales',
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена продажи'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} шт."

    class Meta:
        verbose_name = 'Товар в продаже'
        verbose_name_plural = 'Товары в продажах'
        unique_together = ('sale', 'product')