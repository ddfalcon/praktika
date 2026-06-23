from django.contrib import admin
from .models import Category, Product, Order, OrderItem, ContactMessage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'old_price', 'in_stock', 'is_featured')
    list_filter = ('category', 'in_stock', 'is_featured')
    list_editable = ('price', 'in_stock', 'is_featured')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'price', 'quantity', 'subtotal')

    def subtotal(self, obj):
        return obj.subtotal
    subtotal.short_description = 'Сумма'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'status', 'total', 'created_at')
    list_filter = ('status', 'created_at')
    list_editable = ('status',)
    search_fields = ('name', 'email', 'phone')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at',)

    def total(self, obj):
        return f'{obj.total} ₽'
    total.short_description = 'Итого'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    list_editable = ('is_read',)
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at',)
