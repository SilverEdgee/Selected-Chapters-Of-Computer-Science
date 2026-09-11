from decimal import Decimal, ROUND_HALF_UP
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.templatetags.static import static
from django.utils import timezone
PHONE_VALIDATOR = RegexValidator(
    regex=r'^\+375 \(29\) \d{3}-\d{2}-\d{2}$',
    message='Телефон должен быть в формате +375 (29) XXX-XX-XX',
)
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True
class ProductType(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name
class ToyModel(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name
class Tag(TimeStampedModel):
    name = models.CharField(max_length=80, unique=True)
    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name
class Product(TimeStampedModel):
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=200)
    product_type = models.ForeignKey(ProductType, on_delete=models.PROTECT, related_name='products')
    toy_model = models.ForeignKey(ToyModel, on_delete=models.PROTECT, related_name='products')
    tags = models.ManyToManyField(Tag, blank=True, related_name='products')
    description = models.TextField(blank=True)
    image = models.FileField(upload_to='products/', blank=True, null=True)
    image_url = models.URLField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ['name']
    def clean(self):
        super().clean()
        if self.price is not None and self.price <= 0:
            raise ValidationError({'price': 'Цена должна быть положительной.'})
    def __str__(self):
        return f'{self.name} ({self.code})'

    @property
    def image_source(self):
        if self.image:
            return self.image.url
        return self.image_url
class Client(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='client_profile')
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, validators=[PHONE_VALIDATOR])
    city = models.CharField(max_length=120)
    address = models.CharField(max_length=255)
    birth_date = models.DateField()
    notes = models.TextField(blank=True)
    class Meta:
        ordering = ['full_name']
    def clean(self):
        super().clean()
        if self.birth_date:
            today = timezone.localdate()
            age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
            if age < 18:
                raise ValidationError({'birth_date': 'Клиент должен быть старше 18 лет.'})
    @property
    def age(self):
        today = timezone.localdate()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
    def __str__(self):
        return self.full_name
class Employee(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee_profile')
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, validators=[PHONE_VALIDATOR])
    position = models.CharField(max_length=120)
    specialization = models.CharField(max_length=120, blank=True)
    birth_date = models.DateField()
    class Meta:
        ordering = ['full_name']
    def clean(self):
        super().clean()
        if self.birth_date:
            today = timezone.localdate()
            age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
            if age < 18:
                raise ValidationError({'birth_date': 'Сотрудник должен быть старше 18 лет.'})
    @property
    def age(self):
        today = timezone.localdate()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
    def __str__(self):
        return self.full_name
class Sale(TimeStampedModel):
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='sales')
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    promo_code = models.ForeignKey('PromoCode', on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    sale_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    discount_percent = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(100)])
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    products = models.ManyToManyField(Product, through='SaleItem', related_name='sales')
    class Meta:
        ordering = ['-sale_date']
    def recalculate_total(self):
        subtotal = sum((item.line_total for item in self.items.all()), Decimal('0.00'))
        discount = Decimal(self.discount_percent or 0) / Decimal('100')
        total = (subtotal * (Decimal('1.00') - discount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.total_amount = total
        self.save(update_fields=['total_amount', 'updated_at'])
        return total
    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields')
        super().save(*args, **kwargs)
        if update_fields is not None:
            update_fields = set(update_fields)
        if self.pk and self.items.exists() and (update_fields is None or update_fields & {'promo_code', 'discount_percent', 'client', 'employee', 'sale_date', 'notes'}):
            if not (update_fields is not None and update_fields <= {'total_amount', 'updated_at'}):
                self.recalculate_total()
    def __str__(self):
        return f'Продажа #{self.pk or "новая"} — {self.client.full_name}'
class SaleItem(TimeStampedModel):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='sale_items')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    class Meta:
        ordering = ['id']
        unique_together = [('sale', 'product')]
    @property
    def line_total(self):
        return self.quantity * self.unit_price
    def save(self, *args, **kwargs):
        if not self.unit_price and self.product_id:
            self.unit_price = self.product.price
        super().save(*args, **kwargs)
        self.sale.recalculate_total()
    def delete(self, *args, **kwargs):
        sale = self.sale
        super().delete(*args, **kwargs)
        sale.recalculate_total()
    def __str__(self):
        return f'{self.product.name} x {self.quantity}'
class CompanyInfo(TimeStampedModel):
    title = models.CharField(max_length=200, default='Фабрика игрушек')
    description = models.TextField()
    mission = models.TextField(blank=True)
    requisites = models.TextField(blank=True)
    logo = models.FileField(upload_to='company/', blank=True, null=True)
    logo_url = models.URLField(blank=True)
    video_url = models.URLField(blank=True)
    certificate_text = models.TextField(blank=True)
    certificate_image = models.FileField(upload_to='company/certificates/', blank=True, null=True)
    certificate_image_static_path = models.CharField(max_length=255, blank=True)
    class Meta:
        ordering = ['title']
    def __str__(self):
        return self.title

    @property
    def logo_source(self):
        if self.logo:
            return self.logo.url
        return self.logo_url

    @property
    def certificate_image_source(self):
        if self.certificate_image:
            return self.certificate_image.url
        if self.certificate_image_static_path:
            return static(self.certificate_image_static_path)
        return ''

    @property
    def certificate_image_small_source(self):
        if self.certificate_image_static_path:
            return static(self.certificate_image_static_path.replace('-720.webp', '-420.webp'))
        return self.certificate_image_source


class CompanyMilestone(TimeStampedModel):
    company = models.ForeignKey(CompanyInfo, on_delete=models.CASCADE, related_name='milestones')
    year = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=160)
    description = models.TextField()

    class Meta:
        ordering = ['year']
        unique_together = [('company', 'year')]

    def __str__(self):
        return f'{self.year} — {self.title}'


class Partner(TimeStampedModel):
    name = models.CharField(max_length=160, unique=True)
    website = models.URLField()
    description = models.CharField(max_length=255, blank=True)
    logo = models.FileField(upload_to='partners/', blank=True, null=True)
    logo_url = models.URLField(blank=True)
    logo_static_path = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def logo_source(self):
        if self.logo:
            return self.logo.url
        return self.logo_url
class NewsArticle(TimeStampedModel):
    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=255)
    body = models.TextField()
    image = models.FileField(upload_to='news/', blank=True, null=True)
    image_url = models.URLField(blank=True)
    image_static_path = models.CharField(max_length=255, blank=True)
    published_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)
    class Meta:
        ordering = ['-published_at']
    def __str__(self):
        return self.title
    @property
    def image_source(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        if self.image_static_path:
            return static(self.image_static_path)
        return ''

    @property
    def image_small_source(self):
        if self.image_static_path:
            return static(self.image_static_path.replace('-720.webp', '-360.webp'))
        return self.image_source
class FAQEntry(TimeStampedModel):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    class Meta:
        ordering = ['question']
    def __str__(self):
        return self.question
class ContactPerson(TimeStampedModel):
    full_name = models.CharField(max_length=200)
    role = models.CharField(max_length=120)
    phone = models.CharField(max_length=20, validators=[PHONE_VALIDATOR])
    email = models.EmailField()
    description = models.TextField(blank=True)
    photo = models.FileField(upload_to='contacts/', blank=True, null=True)
    photo_url = models.URLField(blank=True)
    class Meta:
        ordering = ['full_name']
    def __str__(self):
        return f'{self.full_name} — {self.role}'
    @property
    def photo_source(self):
        if self.photo:
            return self.photo.url
        return self.photo_url
class Vacancy(TimeStampedModel):
    title = models.CharField(max_length=200)
    description = models.TextField()
    salary = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ['title']
    def __str__(self):
        return self.title
class Review(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    name = models.CharField(max_length=200)
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    text = models.TextField()
    is_approved = models.BooleanField(default=True)
    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        return f'{self.name} ({self.rating}/5)'
class PromoCode(TimeStampedModel):
    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255)
    discount_percent = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    valid_from = models.DateField(null=True, blank=True)
    valid_to = models.DateField(null=True, blank=True)
    class Meta:
        ordering = ['code']
    def clean(self):
        super().clean()
        if self.discount_percent > 100:
            raise ValidationError({'discount_percent': 'Скидка не может быть больше 100%.'})
    def is_available(self):
        today = timezone.localdate()
        if not self.is_active or self.is_archived:
            return False
        if self.valid_from and today < self.valid_from:
            return False
        if self.valid_to and today > self.valid_to:
            return False
        return True
    def __str__(self):
        return self.code
