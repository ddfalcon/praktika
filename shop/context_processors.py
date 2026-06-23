from .cart import Cart
from .models import Category


def cart_summary(request):
    cart = Cart(request)
    return {'cart_count': len(cart), 'cart_total': cart.total}


def categories_menu(request):
    return {'menu_categories': Category.objects.all()}
