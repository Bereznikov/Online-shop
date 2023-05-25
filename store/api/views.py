from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticated


from products.models import Product, Basket
from products.serializers import ProductSerializer, BasketSerializer


class ProductModelAPIViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'destroy'):
            self.permission_classes = (IsAdminUser,)
        return super(ProductModelAPIViewSet, self).get_permissions()


class BasketModelAPIViewSet(ModelViewSet):
    queryset = Basket.objects.all()
    serializer_class = BasketSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    def get_queryset(self):
        queryset = super(BasketModelAPIViewSet, self).get_queryset()
        return queryset.filter(user=self.request.user)
