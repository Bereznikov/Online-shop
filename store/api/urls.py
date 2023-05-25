from django.urls import path, include

from rest_framework import routers

from api.views import ProductModelAPIViewSet, BasketModelAPIViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'products', ProductModelAPIViewSet)
router.register(r'baskets', BasketModelAPIViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
