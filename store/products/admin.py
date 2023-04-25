from django.contrib import admin

from products.models import Basket, Product, ProductCategory, ProductSection

admin.site.register(ProductCategory)
admin.site.register(ProductSection)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category')
    fields = ('name', 'price', 'image', 'category')
    search_fields = ('id',)
    ordering = ('id',)


class BasketAdmin(admin.TabularInline):
    model = Basket
    fields = ('product', 'quantity', 'created_timestamp')
    readonly_fields = ('created_timestamp',)
    extra = 0
