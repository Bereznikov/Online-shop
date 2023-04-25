from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

from common.views import TitleMixin
from products.models import Basket, Product, ProductCategory, ProductSection


class IndexView(TitleMixin, TemplateView):
    template_name = 'products/index.html'
    title = 'Store'


class ProductsListView(TitleMixin, ListView):
    model = Product
    template_name = 'products/products.html'
    paginate_by = 30
    title = 'Store - Каталог'

    def get_queryset(self):
        queryset = super(ProductsListView, self).get_queryset()
        section_id = self.kwargs.get('section_id')
        category_id = self.kwargs.get('category_id')
        if category_id:
            return queryset.filter(category_id=category_id)
        elif section_id:
            return queryset.filter(section_id=section_id)
        else:
            return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        section_id = self.kwargs.get('section_id')
        context = super(ProductsListView, self).get_context_data()
        context['categories'] = ProductCategory.objects.filter(section_id=section_id)
        context['sections'] = ProductSection.objects.all()
        return context


@login_required()
def basket_add(request, product_id):
    product = Product.objects.get(id=product_id)
    baskets = Basket.objects.filter(user=request.user, product=product)

    if not baskets.exists():
        Basket.objects.create(user=request.user, product=product, quantity=1)
    else:
        basket = baskets.first()
        basket.quantity += 1
        basket.save()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required()
def basket_remove(request, basket_id):
    basket = Basket.objects.get(id=basket_id)
    basket.delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
