from datetime import timedelta
import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone


def _shift_years(value, years):
    try:
        return value.replace(year=value.year - years)
    except ValueError:  # 29 февраля в невисокосный год
        return value.replace(year=value.year - years, day=28)


def adult_birth_date_bounds():
    today = timezone.localdate()
    return _shift_years(today, 120).isoformat(), _shift_years(today, 18).isoformat()
from .models import (
    Client,
    CompanyMilestone,
    CompanyInfo,
    ContactPerson,
    Employee,
    FAQEntry,
    NewsArticle,
    Partner,
    Product,
    ProductType,
    PromoCode,
    Review,
    Sale,
    SaleItem,
    Tag,
    ToyModel,
    Vacancy,
)
class BootstrapLikeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (css + ' form-control').strip()
class AdultValidationMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'birth_date' in self.fields:
            min_date, max_date = adult_birth_date_bounds()
            self.fields['birth_date'].widget.attrs.update({'min': min_date, 'max': max_date})

    def clean_birth_date(self):
        birth_date = self.cleaned_data['birth_date']
        today = timezone.localdate()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        if age < 18:
            raise forms.ValidationError('Возраст должен быть 18+.')
        return birth_date
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(label='ФИО')
    phone = forms.CharField(label='Телефон')
    city = forms.CharField(label='Город')
    address = forms.CharField(label='Адрес')
    birth_date = forms.DateField(label='Дата рождения', widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'full_name', 'phone', 'city', 'address', 'birth_date')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        min_date, max_date = adult_birth_date_bounds()
        self.fields['birth_date'].widget.attrs.update({'min': min_date, 'max': max_date})
        self.fields['phone'].widget.attrs.update({'pattern': r'\+375 \(29\) \d{3}-\d{2}-\d{2}', 'placeholder': '+375 (29) XXX-XX-XX'})
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
    def clean_birth_date(self):
        birth_date = self.cleaned_data['birth_date']
        today = timezone.localdate()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        if age < 18:
            raise forms.ValidationError('Пользователю должно быть 18+ лет.')
        return birth_date
class ProductTypeForm(BootstrapLikeForm):
    class Meta:
        model = ProductType
        fields = ['name', 'description']
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}
class ToyModelForm(BootstrapLikeForm):
    class Meta:
        model = ToyModel
        fields = ['name', 'description']
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}
class TagForm(BootstrapLikeForm):
    class Meta:
        model = Tag
        fields = ['name']
class ProductForm(BootstrapLikeForm):
    class Meta:
        model = Product
        fields = ['code', 'name', 'product_type', 'toy_model', 'tags', 'description', 'image', 'image_url', 'price', 'is_active']
        widgets = {
            'tags': forms.CheckboxSelectMultiple(),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
class ClientForm(AdultValidationMixin, BootstrapLikeForm):
    class Meta:
        model = Client
        fields = ['user', 'full_name', 'phone', 'city', 'address', 'birth_date', 'notes']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'phone': forms.TextInput(attrs={'pattern': r'\+375 \(29\) \d{3}-\d{2}-\d{2}'}),
        }
class EmployeeForm(AdultValidationMixin, BootstrapLikeForm):
    class Meta:
        model = Employee
        fields = ['user', 'full_name', 'phone', 'position', 'specialization', 'birth_date']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'phone': forms.TextInput(attrs={'pattern': r'\+375 \(29\) \d{3}-\d{2}-\d{2}'}),
        }
class SaleForm(BootstrapLikeForm):
    class Meta:
        model = Sale
        fields = ['client', 'employee', 'promo_code', 'discount_percent', 'sale_date', 'notes']
        widgets = {
            'sale_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
class SaleItemForm(BootstrapLikeForm):
    class Meta:
        model = SaleItem
        fields = ['sale', 'product', 'quantity', 'unit_price']
class CompanyInfoForm(BootstrapLikeForm):
    class Meta:
        model = CompanyInfo
        fields = ['title', 'description', 'mission', 'requisites', 'logo', 'logo_url', 'video_url', 'certificate_text', 'certificate_image', 'certificate_image_static_path']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'mission': forms.Textarea(attrs={'rows': 3}),
            'requisites': forms.Textarea(attrs={'rows': 3}),
            'certificate_text': forms.Textarea(attrs={'rows': 4}),
        }


class CompanyMilestoneForm(BootstrapLikeForm):
    class Meta:
        model = CompanyMilestone
        fields = ['company', 'year', 'title', 'description']
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}


class PartnerForm(BootstrapLikeForm):
    class Meta:
        model = Partner
        fields = ['name', 'website', 'description', 'logo', 'logo_url', 'logo_static_path', 'is_active']
class NewsArticleForm(BootstrapLikeForm):
    class Meta:
        model = NewsArticle
        fields = ['title', 'summary', 'body', 'image', 'image_url', 'image_static_path', 'published_at', 'is_published']
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 2}),
            'body': forms.Textarea(attrs={'rows': 5}),
            'published_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
class FAQEntryForm(BootstrapLikeForm):
    class Meta:
        model = FAQEntry
        fields = ['question', 'answer']
        widgets = {'answer': forms.Textarea(attrs={'rows': 4})}
class ContactPersonForm(BootstrapLikeForm):
    class Meta:
        model = ContactPerson
        fields = ['full_name', 'role', 'phone', 'email', 'description', 'photo', 'photo_url']
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}
class VacancyForm(BootstrapLikeForm):
    class Meta:
        model = Vacancy
        fields = ['title', 'description', 'salary', 'is_active']
        widgets = {'description': forms.Textarea(attrs={'rows': 4})}
class ReviewForm(BootstrapLikeForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {'text': forms.Textarea(attrs={'rows': 4})}
class PromoCodeForm(BootstrapLikeForm):
    class Meta:
        model = PromoCode
        fields = ['code', 'description', 'discount_percent', 'is_active', 'is_archived', 'valid_from', 'valid_to']
        widgets = {
            'valid_from': forms.DateInput(attrs={'type': 'date'}),
            'valid_to': forms.DateInput(attrs={'type': 'date'}),
        }
class PurchaseForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1, label='Количество')
    promo_code = forms.CharField(required=False, label='Промокод')

    def clean_promo_code(self):
        code = self.cleaned_data.get('promo_code', '').strip()
        if not code:
            self.promo_code_object = None
            return ''
        from .models import PromoCode

        promo = PromoCode.objects.filter(code__iexact=code).first()
        if promo is None or not promo.is_available():
            raise forms.ValidationError('Промокод не найден или недействителен.')
        self.promo_code_object = promo
        return promo.code


class CheckoutForm(forms.Form):
    PAYMENT_CHOICES = [
        ('card', 'Банковская карта'),
        ('cash', 'Наличными при получении'),
    ]
    DELIVERY_TIME_CHOICES = [
        ('morning', '09:00–13:00'),
        ('day', '13:00–17:00'),
        ('evening', '17:00–21:00'),
    ]

    full_name = forms.CharField(label='Получатель', min_length=3, max_length=200)
    email = forms.EmailField(label='Email для чека')
    phone = forms.RegexField(
        label='Телефон',
        regex=r'^\+375 \(29\) \d{3}-\d{2}-\d{2}$',
        error_messages={'invalid': 'Введите телефон в формате +375 (29) XXX-XX-XX.'},
        widget=forms.TextInput(attrs={
            'placeholder': '+375 (29) XXX-XX-XX',
            'pattern': r'\+375 \(29\) \d{3}-\d{2}-\d{2}',
            'autocomplete': 'tel',
        }),
    )
    address = forms.CharField(label='Адрес доставки', max_length=255)
    delivery_date = forms.DateField(label='Дата доставки', widget=forms.DateInput(attrs={'type': 'date'}))
    delivery_time = forms.ChoiceField(label='Интервал доставки', choices=DELIVERY_TIME_CHOICES)
    payment_method = forms.ChoiceField(
        label='Способ оплаты',
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect,
    )
    card_number = forms.CharField(
        label='Номер карты', required=False, max_length=19,
        widget=forms.TextInput(attrs={
            'inputmode': 'numeric',
            'autocomplete': 'cc-number',
            'pattern': r'[0-9 ]{16,19}',
            'placeholder': '0000 0000 0000 0000',
        }),
    )
    expiry = forms.CharField(
        label='Срок действия', required=False, max_length=5,
        widget=forms.TextInput(attrs={'pattern': r'(0[1-9]|1[0-2])/[0-9]{2}', 'placeholder': 'MM/YY', 'autocomplete': 'cc-exp'}),
    )
    cvv = forms.CharField(
        label='CVV', required=False, max_length=3,
        widget=forms.PasswordInput(attrs={'inputmode': 'numeric', 'pattern': r'[0-9]{3}', 'autocomplete': 'cc-csc'}),
    )
    promo_code = forms.CharField(label='Промокод', required=False, max_length=50)
    gift_wrap = forms.BooleanField(label='Подарочная упаковка', required=False)
    comment = forms.CharField(label='Комментарий', required=False, widget=forms.Textarea(attrs={'rows': 3}))
    agree = forms.BooleanField(label='Я согласен с политикой конфиденциальности')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tomorrow = timezone.localdate() + timedelta(days=1)
        self.fields['delivery_date'].widget.attrs['min'] = tomorrow.isoformat()
        for field in self.fields.values():
            css = field.widget.attrs.get('class', '')
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                field.widget.attrs['class'] = (css + ' form-control').strip()

    def clean_delivery_date(self):
        value = self.cleaned_data['delivery_date']
        if value <= timezone.localdate():
            raise forms.ValidationError('Дата доставки должна быть не раньше завтрашнего дня.')
        return value

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('payment_method') == 'card':
            number = re.sub(r'\s+', '', cleaned.get('card_number', ''))
            if not re.fullmatch(r'\d{16}', number):
                self.add_error('card_number', 'Введите 16 цифр номера карты.')
            if not re.fullmatch(r'(0[1-9]|1[0-2])/\d{2}', cleaned.get('expiry', '')):
                self.add_error('expiry', 'Введите срок действия в формате MM/YY.')
            if not re.fullmatch(r'\d{3}', cleaned.get('cvv', '')):
                self.add_error('cvv', 'Введите три цифры CVV.')
        code = cleaned.get('promo_code', '').strip()
        self.promo_code_object = None
        if code:
            promo = PromoCode.objects.filter(code__iexact=code).first()
            if promo is None or not promo.is_available():
                self.add_error('promo_code', 'Промокод не найден или недействителен.')
            else:
                self.promo_code_object = promo
                cleaned['promo_code'] = promo.code
        return cleaned
