from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from products.models import Product, ProductCategory, ProductSection


class IndexViewTestCase(TestCase):

    def test_view(self):
        path = reverse('index')
        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], 'Store')
        self.assertTemplateUsed(response, 'products/index.html')


class ProductsListViewTestCase(TestCase):
    fixtures = ['sections_next.json', 'categories_next.json', 'products.json']

    def test_list(self):
        path = reverse('products:index')
        response = self.client.get(path)

        products = Product.objects.all()
        self._common_tests(response)
        self.assertEqual(list(response.context_data['object_list']), list(products[:30]))

    def test_list_section(self):
        section = ProductSection.objects.last()
        path = reverse('products:section', kwargs={'section_id': section.id})
        response = self.client.get(path)

        products = Product.objects.all()
        self._common_tests(response)
        self.assertEqual(
            list(response.context_data['object_list']),
            list(products.filter(section_id=section.id)[:30])
        )

    def test_list_category(self):
        category = ProductCategory.objects.first()
        path = reverse('products:category', kwargs={'category_id': category.id})
        response = self.client.get(path)

        products = Product.objects.all()
        self._common_tests(response)
        self.assertEqual(
            list(response.context_data['object_list']),
            list(products.filter(category_id=category.id)[:30])
        )

    def _common_tests(self, response):
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], 'Store - Каталог')
        self.assertTemplateUsed(response, 'products/products.html')
