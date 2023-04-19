from products.models import Basket


def baskets(request):
    user = request.user
    baskets = Basket.objects.filter(user=user) if user.is_authenticated else []
    total_sum = sum(basket.sum() for basket in baskets)
    total_quantity = sum(basket.quantity for basket in baskets)
    return {'baskets': baskets,
            'total_sum': total_sum,
            'total_quantity': total_quantity
            }
