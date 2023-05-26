from rest_framework import fields, serializers

from products.models import Basket, Product, ProductCategory, ProductSection


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='name', queryset=ProductCategory.objects.all())
    section = serializers.SlugRelatedField(slug_field='name', queryset=ProductSection.objects.all())

    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'quantity', 'image', 'category', 'section')


class BasketSerializer(serializers.ModelSerializer):
    product = ProductSerializer
    sum = fields.FloatField()

    class Meta:
        model = Basket
        fields = ('id', 'product', 'quantity', 'sum', 'created_timestamp')
        read_only_fields = ('created_timestamp',)
