from django.db import models
from django.conf import settings

from users.models import User

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


class ProductSection(models.Model):
    name = models.CharField(max_length=128, unique=True)

    class Meta:
        verbose_name = 'секцию'
        verbose_name_plural = 'Секции продуктов'

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    name = models.CharField(max_length=128)
    section = models.ForeignKey(to=ProductSection, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'категорию'
        verbose_name_plural = 'Категории продуктов'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='media/product_images')
    category = models.ForeignKey(to=ProductCategory, on_delete=models.CASCADE)
    section = models.ForeignKey(to=ProductSection, on_delete=models.CASCADE)
    stripe_product_price_id = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        verbose_name = 'продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return f'Продукт: {self.name} | Категория: {self.category.name}'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.stripe_product_price_id:
            stripe_product_price = self.create_stripe_product_price()
            self.stripe_product_price_id = stripe_product_price['id']
        super(Product, self).save(force_insert=False, force_update=False, using=None, update_fields=None)

    def create_stripe_product_price(self):
        stripe_product = stripe.Product.create(name=self.name)
        stripe_product_price = stripe.Price.create(
            unit_amount=round(self.price * 100),
            currency="kzt",
            product=stripe_product['id'],
        )
        return stripe_product_price


class Basket(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=8)
    created_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Корзина для {self.user.email} | Продукт: {self.product.name}'

    def sum(self):
        return self.product.price * self.quantity


