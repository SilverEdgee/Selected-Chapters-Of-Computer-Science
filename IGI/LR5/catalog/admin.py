from django.contrib import admin
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
class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'created_at')
    search_fields = ('name',)
@admin.register(ToyModel)
class ToyModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'created_at')
    search_fields = ('name',)
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'product_type', 'toy_model', 'price', 'is_active', 'created_at')
    list_filter = ('product_type', 'toy_model', 'is_active', 'tags')
    search_fields = ('code', 'name')
    filter_horizontal = ('tags',)
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone', 'city', 'age', 'user')
    search_fields = ('full_name', 'phone', 'city')
    list_filter = ('city',)
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'position', 'phone', 'age', 'user')
    search_fields = ('full_name', 'position', 'phone')
    list_filter = ('position',)
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'employee', 'promo_code', 'discount_percent', 'sale_date', 'total_amount')
    list_filter = ('sale_date', 'employee')
    search_fields = ('client__full_name', 'employee__full_name')
    inlines = [SaleItemInline]
@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'sale', 'product', 'quantity', 'unit_price')
    search_fields = ('product__name', 'sale__client__full_name')
    list_filter = ('product',)
@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'updated_at')
    search_fields = ('title', 'description')
@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'published_at', 'is_published', 'updated_at')
    list_filter = ('is_published', 'published_at')
    search_fields = ('title', 'summary', 'body')
@admin.register(FAQEntry)
class FAQEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'updated_at')
    search_fields = ('question', 'answer')
@admin.register(ContactPerson)
class ContactPersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'role', 'phone', 'email', 'updated_at')
    search_fields = ('full_name', 'role', 'phone', 'email')
@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'salary', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'description', 'salary')
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'rating', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved')
    search_fields = ('name', 'text')
@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'discount_percent', 'is_active', 'is_archived', 'valid_from', 'valid_to')
    list_filter = ('is_active', 'is_archived')
    search_fields = ('code', 'description')
