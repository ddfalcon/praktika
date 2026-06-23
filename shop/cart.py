from decimal import Decimal
from django.conf import settings
from .models import Product


class Cart:
    """Корзина на основе сессии."""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if cart is None:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update=False):
        pid = str(product.id)
        if pid not in self.cart:
            self.cart[pid] = {'quantity': 0, 'price': str(product.price)}
        if update:
            self.cart[pid]['quantity'] = quantity
        else:
            self.cart[pid]['quantity'] += quantity
        if self.cart[pid]['quantity'] < 1:
            self.remove(product)
        self.save()

    def remove(self, product):
        pid = str(product.id)
        if pid in self.cart:
            del self.cart[pid]
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        self.session[settings.CART_SESSION_ID] = {}
        self.session.modified = True

    def __iter__(self):
        ids = self.cart.keys()
        products = Product.objects.filter(id__in=ids)
        cart = self.cart.copy()
        for product in products:
            item = cart[str(product.id)]
            item['product'] = product
            item['price'] = Decimal(item['price'])
            item['subtotal'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    @property
    def total(self):
        return sum(Decimal(i['price']) * i['quantity'] for i in self.cart.values())
