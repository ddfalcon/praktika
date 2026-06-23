from django import forms
from .models import Order, ContactMessage


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['name', 'email', 'phone', 'address', 'comment']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Иван Иванов'}),
            'email': forms.EmailInput(attrs={'placeholder': 'mail@example.com'}),
            'phone': forms.TextInput(attrs={'placeholder': '+7 (___) ___-__-__'}),
            'address': forms.TextInput(attrs={'placeholder': 'г. Новосибирск, ул. ...'}),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Комментарий к заказу'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        digits = ''.join(c for c in phone if c.isdigit())
        if len(digits) < 10:
            raise forms.ValidationError('Введите корректный номер телефона.')
        return phone


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ваше имя'}),
            'email': forms.EmailInput(attrs={'placeholder': 'mail@example.com'}),
            'message': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Ваше сообщение...'}),
        }
