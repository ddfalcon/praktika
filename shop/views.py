from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category, Order, OrderItem
from .forms import OrderForm, ContactForm
from .cart import Cart


def home(request):
    featured = Product.objects.filter(is_featured=True, in_stock=True)[:4]
    new_products = Product.objects.filter(in_stock=True)[:8]
    categories = Category.objects.all()
    return render(request, 'shop/home.html', {
        'featured': featured,
        'new_products': new_products,
        'categories': categories,
    })


def catalog(request):
    products = Product.objects.filter(in_stock=True)
    categories = Category.objects.all()
    active_category = request.GET.get('category')
    query = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', '')

    if active_category:
        products = products.filter(category__slug=active_category)
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')

    return render(request, 'shop/catalog.html', {
        'products': products,
        'categories': categories,
        'active_category': active_category,
        'query': query,
        'sort': sort,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related = Product.objects.filter(
        category=product.category, in_stock=True
    ).exclude(id=product.id)[:4]
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'related': related,
    })


def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product, quantity=quantity)
    messages.success(request, f'«{product.name}» добавлен в корзину.')
    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('shop:cart_detail')


def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('shop:cart_detail')


def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product, quantity=quantity, update=True)
    return redirect('shop:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'shop/cart.html', {'cart': cart})


def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.info(request, 'Корзина пуста — сначала добавьте товары.')
        return redirect('shop:catalog')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    product_name=item['product'].name,
                    price=item['price'],
                    quantity=item['quantity'],
                )
            cart.clear()
            return render(request, 'shop/order_success.html', {'order': order})
    else:
        form = OrderForm()
    return render(request, 'shop/checkout.html', {'form': form, 'cart': cart})


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Сообщение отправлено! Мы свяжемся с вами.')
            return redirect('shop:contact')
    else:
        form = ContactForm()
    return render(request, 'shop/contact.html', {'form': form})


def about(request):
    return render(request, 'shop/about.html')
