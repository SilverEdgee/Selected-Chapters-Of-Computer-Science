from datetime import date
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
    """Границы для HTML5-валидации даты рождения на фронте: 18+ и не старше 120 лет."""
    today = timezone.localdate()
    return _shift_years(today, 120).isoformat(), _shift_years(today, 18).isoformat()
from .models import (
    Client,
    CompanyInfo,
    ContactPerson,
    Employee,
    FAQEntry,
    NewsArticle,
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
        fields = ['code', 'name', 'product_type', 'toy_model', 'tags', 'price', 'is_active']
        widgets = {'tags': forms.CheckboxSelectMultiple()}
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
        fields = ['title', 'description', 'mission', 'requisites']
        widgets = {'description': forms.Textarea(attrs={'rows': 4}), 'mission': forms.Textarea(attrs={'rows': 3}), 'requisites': forms.Textarea(attrs={'rows': 3})}
class NewsArticleForm(BootstrapLikeForm):
    class Meta:
        model = NewsArticle
        fields = ['title', 'summary', 'body', 'image', 'image_url', 'published_at', 'is_published']
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
