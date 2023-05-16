from django.contrib import admin

from products.models import Basket, Product, ProductCategory, ProductSection

admin.site.register(ProductCategory)
admin.site.register(ProductSection)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'section', 'category', 'stripe_product_price_id')
    fields = ('name', 'price', 'image', 'section', 'category', 'stripe_product_price_id')
    search_fields = ('id',)
    ordering = ('id',)


class BasketAdmin(admin.TabularInline):
    model = Basket
    fields = ('product', 'quantity', 'created_timestamp')
    readonly_fields = ('created_timestamp',)
    extra = 0
