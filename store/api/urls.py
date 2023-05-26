from django.urls import include, path
from rest_framework import routers

from api.views import BasketModelAPIViewSet, ProductModelAPIViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'products', ProductModelAPIViewSet)
router.register(r'baskets', BasketModelAPIViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
