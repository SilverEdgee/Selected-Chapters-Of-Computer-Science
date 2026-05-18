import logging
import json
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Avg, Q, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from .forms import (
    ClientForm,
    CompanyInfoForm,
    ContactPersonForm,
    EmployeeForm,
    FAQEntryForm,
    NewsArticleForm,
    ProductForm,
    ProductTypeForm,
    PromoCodeForm,
    PurchaseForm,
    RegistrationForm,
    ReviewForm,
    SaleForm,
    SaleItemForm,
    TagForm,
    ToyModelForm,
    VacancyForm,
)
from .services import fetch_external_api_results
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
logger = logging.getLogger(__name__)
def is_staff_user(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)
MODEL_SPECS = {
    'product-types': {'model': ProductType, 'form': ProductTypeForm, 'title': 'Типы игрушек'},
    'toy-models': {'model': ToyModel, 'form': ToyModelForm, 'title': 'Модели игрушек'},
    'tags': {'model': Tag, 'form': TagForm, 'title': 'Теги'},
    'products': {'model': Product, 'form': ProductForm, 'title': 'Товары'},
    'clients': {'model': Client, 'form': ClientForm, 'title': 'Клиенты'},
    'employees': {'model': Employee, 'form': EmployeeForm, 'title': 'Сотрудники'},
    'sales': {'model': Sale, 'form': SaleForm, 'title': 'Продажи'},
    'sale-items': {'model': SaleItem, 'form': SaleItemForm, 'title': 'Позиции продаж'},
    'company-info': {'model': CompanyInfo, 'form': CompanyInfoForm, 'title': 'О компании'},
    'news': {'model': NewsArticle, 'form': NewsArticleForm, 'title': 'Новости'},
    'faq': {'model': FAQEntry, 'form': FAQEntryForm, 'title': 'Словарь терминов и понятий'},
    'contacts': {'model': ContactPerson, 'form': ContactPersonForm, 'title': 'Контакты'},
    'vacancies': {'model': Vacancy, 'form': VacancyForm, 'title': 'Вакансии'},
    'reviews': {'model': Review, 'form': ReviewForm, 'title': 'Отзывы'},
    'promo-codes': {'model': PromoCode, 'form': PromoCodeForm, 'title': 'Промокоды и купоны'},
}
def get_spec(model_key):
    if model_key not in MODEL_SPECS:
        raise ValueError(f'Неизвесная сущность: {model_key}')
    return MODEL_SPECS[model_key]
def page_context(**kwargs):
    ctx = {'current_dt': timezone.now()}
    ctx.update(kwargs)
    return ctx
def home(request):
    latest_article = NewsArticle.objects.filter(is_published=True).order_by('-published_at').first()
    latest_product = Product.objects.select_related('product_type', 'toy_model').prefetch_related('tags').order_by('-created_at').first()
    stats = {
        'products': Product.objects.count(),
        'clients': Client.objects.count(),
        'employees': Employee.objects.count(),
        'sales': Sale.objects.count(),
        'revenue': Sale.objects.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00'),
    }
    monthly = (
        Sale.objects.annotate(month=TruncMonth('sale_date'))
        .values('month')
        .annotate(total=Sum('total_amount'))
        .order_by('-month')[:6]
    )
    monthly_chart = [
        {'label': timezone.localtime(item['month']).strftime('%m/%Y') if item['month'] else '—', 'value': float(item['total'] or Decimal('0.00'))}
        for item in reversed(list(monthly))
    ]
    return render(
        request,
        'catalog/home.html',
        page_context(
            latest_article=latest_article,
            latest_product=latest_product,
            stats=stats,
            monthly_chart=monthly_chart,
            monthly_chart_labels_json=json.dumps([row['label'] for row in monthly_chart], ensure_ascii=False),
            monthly_chart_values_json=json.dumps([row['value'] for row in monthly_chart]),
        ),
    )
def about(request):
    return render(request, 'catalog/about.html', page_context(company=CompanyInfo.objects.first()))
def news_list(request):
    articles = NewsArticle.objects.filter(is_published=True)
    paginator = Paginator(articles, 5)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'catalog/news_list.html', page_context(articles=page_obj, page_obj=page_obj))
def news_detail(request, pk):
    article = get_object_or_404(NewsArticle, pk=pk, is_published=True)
    return render(request, 'catalog/news_detail.html', page_context(article=article))
def glossary(request):
    return render(request, 'catalog/glossary.html', page_context(entries=FAQEntry.objects.all()))
def contacts(request):
    return render(request, 'catalog/contacts.html', page_context(contacts=ContactPerson.objects.all()))
def privacy(request):
    return render(request, 'catalog/privacy.html', page_context())
def vacancies(request):
    return render(request, 'catalog/vacancies.html', page_context(vacancies=Vacancy.objects.filter(is_active=True)))
@require_http_methods(['GET', 'POST'])
def reviews(request):
    review_list = Review.objects.filter(is_approved=True)
    form = ReviewForm()
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Чтобы добавить отзыв, нужно войти в аккаунт.')
            return redirect('login')
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.name = request.user.get_full_name() or request.user.username
            review.save()
            messages.success(request, 'Отзыв сохранён.')
            return redirect('catalog:reviews')
    return render(request, 'catalog/reviews.html', page_context(reviews=review_list, form=form))
def promo_codes(request):
    active = [promo for promo in PromoCode.objects.filter(is_active=True, is_archived=False) if promo.is_available()]
    archive = PromoCode.objects.filter(is_archived=True)
    return render(request, 'catalog/promo_codes.html', page_context(active_promo_codes=active, archived_promo_codes=archive))
def product_list(request):
    queryset = Product.objects.select_related('product_type', 'toy_model').prefetch_related('tags')
    query = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', 'name')
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query)
            | Q(code__icontains=query)
            | Q(product_type__name__icontains=query)
            | Q(toy_model__name__icontains=query)
            | Q(tags__name__icontains=query)
        ).distinct()
    allowed_sort = {'name', '-name', 'price', '-price', 'created_at', '-created_at'}
    if sort not in allowed_sort:
        sort = 'name'
    queryset = queryset.order_by(sort)
    paginator = Paginator(queryset, 5)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'catalog/product_list.html', page_context(products=page_obj, page_obj=page_obj, query=query, sort=sort))
def product_detail_by_code(request, code):
    product = get_object_or_404(Product.objects.select_related('product_type', 'toy_model').prefetch_related('tags'), code=code)
    return product_detail(request, product.pk)
@require_http_methods(['GET', 'POST'])
def product_detail(request, pk):
    product = get_object_or_404(Product.objects.select_related('product_type', 'toy_model').prefetch_related('tags'), pk=pk)
    purchase_form = PurchaseForm(request.POST or None)
    if request.method == 'POST':
        if not request.user.is_authenticated or not hasattr(request.user, 'client_profile') or request.user.client_profile is None:
            messages.error(request, 'Покупка доступна только зарегистрированному клиенту.')
            return redirect('login')
        if purchase_form.is_valid():
            client = request.user.client_profile
            quantity = purchase_form.cleaned_data['quantity']
            promo = getattr(purchase_form, 'promo_code_object', None)
            discount_percent = promo.discount_percent if promo else 0
            with transaction.atomic():
                sale = Sale.objects.create(client=client, promo_code=promo, discount_percent=discount_percent)
                SaleItem.objects.create(sale=sale, product=product, quantity=quantity, unit_price=product.price)
            logger.info('Создана покупка product=%s client=%s qty=%s promo=%s discount=%s', product.pk, client.pk, quantity, getattr(promo, 'code', None), discount_percent)
            messages.success(request, 'Покупка сохранена.')
            return redirect('catalog:dashboard')
    return render(request, 'catalog/product_detail.html', page_context(product=product, purchase_form=purchase_form))
def stats(request):
    revenue = Sale.objects.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    avg_sale = Sale.objects.aggregate(avg=Avg('total_amount'))['avg'] or Decimal('0.00')
    top_products = (
        SaleItem.objects.values('product__name')
        .annotate(total_qty=Sum('quantity'))
        .order_by('-total_qty', 'product__name')[:10]
    )
    monthly_sales = (
        Sale.objects.annotate(month=TruncMonth('sale_date'))
        .values('month')
        .annotate(total=Sum('total_amount'))
        .order_by('month')
    )
    monthly_sales_chart = [
        {'label': timezone.localtime(row['month']).strftime('%m/%Y') if row['month'] else '—', 'value': float(row['total'] or Decimal('0.00'))}
        for row in monthly_sales
    ]
    return render(
        request,
        'catalog/stats.html',
        page_context(
            revenue=revenue,
            avg_sale=avg_sale,
            top_products=top_products,
            monthly_sales=monthly_sales,
            monthly_sales_labels_json=json.dumps([row['label'] for row in monthly_sales_chart], ensure_ascii=False),
            monthly_sales_values_json=json.dumps([row['value'] for row in monthly_sales_chart]),
        ),
    )
@login_required
def api_demo(request):
    endpoints = [
        ('Chuck Norris', 'https://api.chucknorris.io/jokes/random'),
        ('Agify', 'https://api.agify.io/?name=anna'),
    ]
    api_results = fetch_external_api_results(endpoints)
    return render(request, 'catalog/api_demo.html', page_context(api_results=api_results))
@login_required
def api_summary(request):
    data = {
        'products': Product.objects.count(),
        'clients': Client.objects.count(),
        'employees': Employee.objects.count(),
        'sales': Sale.objects.count(),
        'revenue': str(Sale.objects.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')),
    }
    return JsonResponse(data)
@login_required
def dashboard(request):
    if request.user.is_staff or request.user.is_superuser:
        sales = Sale.objects.select_related('client', 'employee').prefetch_related('items__product')
        profile = getattr(request.user, 'employee_profile', None)
    else:
        profile = getattr(request.user, 'client_profile', None)
        sales = Sale.objects.none()
        if profile is not None:
            sales = Sale.objects.select_related('client', 'employee').prefetch_related('items__product').filter(client=profile)
    return render(request, 'catalog/dashboard.html', page_context(profile=profile, sales=sales))
@require_http_methods(['GET', 'POST'])
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Client.objects.create(
                user=user,
                full_name=form.cleaned_data['full_name'],
                phone=form.cleaned_data['phone'],
                city=form.cleaned_data['city'],
                address=form.cleaned_data['address'],
                birth_date=form.cleaned_data['birth_date'],
            )
            login(request, user)
            messages.success(request, 'Регистрация завершена.')
            logger.info('Создан пользователь %s', user.username)
            return redirect('catalog:dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'catalog/register.html', page_context(form=form))
@login_required
@user_passes_test(is_staff_user)
def model_list(request, model_key):
    spec = get_spec(model_key)
    objects = spec['model'].objects.all()
    return render(request, 'catalog/generic_list.html', page_context(model_key=model_key, title=spec['title'], objects=objects))
@login_required
@user_passes_test(is_staff_user)
def model_create(request, model_key):
    spec = get_spec(model_key)
    form_class = spec['form']
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save()
            logger.info('Создан объект %s: %s', model_key, obj)
            messages.success(request, 'Объект создан.')
            return redirect('catalog:model_list', model_key=model_key)
    else:
        form = form_class()
    return render(request, 'catalog/form.html', page_context(title=f'Создать: {spec["title"]}', form=form, submit_label='Сохранить'))
@login_required
@user_passes_test(is_staff_user)
def model_update(request, model_key, pk):
    spec = get_spec(model_key)
    obj = get_object_or_404(spec['model'], pk=pk)
    form_class = spec['form']
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            obj = form.save()
            logger.info('Обновлён объект %s: %s', model_key, obj)
            messages.success(request, 'Изменения сохранены.')
            return redirect('catalog:model_list', model_key=model_key)
    else:
        form = form_class(instance=obj)
    return render(request, 'catalog/form.html', page_context(title=f'Редактировать: {obj}', form=form, submit_label='Обновить'))
@login_required
@user_passes_test(is_staff_user)
def model_delete(request, model_key, pk):
    spec = get_spec(model_key)
    obj = get_object_or_404(spec['model'], pk=pk)
    if request.method == 'POST':
        logger.info('Удалён объект %s: %s', model_key, obj)
        obj.delete()
        messages.success(request, 'Объект удалён.')
        return redirect('catalog:model_list', model_key=model_key)
    return render(request, 'catalog/confirm_delete.html', page_context(object=obj, title=f'Удалить: {obj}'))
