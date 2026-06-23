from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField('Название', max_length=100, unique=True)
    slug = models.SlugField('URL-метка', max_length=120, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:catalog') + f'?category={self.slug}'


class Product(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE,
        related_name='products', verbose_name='Категория'
    )
    name = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL-метка', max_length=220, unique=True)
    description = models.TextField('Описание', blank=True)
    price = models.DecimalField('Цена, ₽', max_digits=10, decimal_places=2)
    old_price = models.DecimalField(
        'Старая цена, ₽', max_digits=10, decimal_places=2,
        null=True, blank=True
    )
    image = models.ImageField('Изображение', upload_to='products/', blank=True)
    in_stock = models.BooleanField('В наличии', default=True)
    is_featured = models.BooleanField('Рекомендуемый', default=False)
    created_at = models.DateTimeField('Добавлен', auto_now_add=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.slug])

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return round((1 - self.price / self.old_price) * 100)
        return 0


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('done', 'Выполнен'),
        ('canceled', 'Отменён'),
    ]
    name = models.CharField('Имя', max_length=120)
    email = models.EmailField('E-mail')
    phone = models.CharField('Телефон', max_length=30)
    address = models.CharField('Адрес доставки', max_length=255)
    comment = models.TextField('Комментарий', blank=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ #{self.pk} — {self.name}'

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField('Товар', max_length=200)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField('Количество', default=1)

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self):
        return f'{self.product_name} × {self.quantity}'

    @property
    def subtotal(self):
        return self.price * self.quantity


class ContactMessage(models.Model):
    name = models.CharField('Имя', max_length=120)
    email = models.EmailField('E-mail')
    message = models.TextField('Сообщение')
    is_read = models.BooleanField('Прочитано', default=False)
    created_at = models.DateTimeField('Отправлено', auto_now_add=True)

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения (обратная связь)'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.created_at:%d.%m.%Y}'
