from django.urls import path
from django.views.decorators.cache import cache_page

from products.views import (ProductDetailView, ProductsListView, basket_add,
                            basket_remove)

app_name = 'products'

urlpatterns = [
    path('', ProductsListView.as_view(), name='index'),
    path('section/<int:section_id>/', ProductsListView.as_view(), name='section'),
    path('category/<int:category_id>/', ProductsListView.as_view(), name='category'),
    path('page/<int:page>/', ProductsListView.as_view(), name='paginator'),
    path('baskets/add/<int:product_id>/', basket_add, name='basket_add'),
    path('baskets/remove/<int:basket_id>/', basket_remove, name='basket_remove'),
    path('product/<int:pk>/', cache_page(30)(ProductDetailView.as_view()), name='product'),
]
