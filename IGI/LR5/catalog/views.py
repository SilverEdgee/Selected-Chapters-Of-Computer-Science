import logging
import json
import io
import base64
from decimal import Decimal
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.contrib import messages
from django.contrib.auth import login
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Avg, Q, Sum, Count, F
from django.db.models.functions import TruncMonth, TruncYear
from django.db.models.functions import Coalesce
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


def is_superuser_user(user):
    return user.is_authenticated and user.is_superuser


def can_manage_model(user, model_key):
    # Only superusers can manage models now (employees are not allowed CRUD)
    return user.is_authenticated and user.is_superuser
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
    stats = None
    monthly_chart = []
    monthly_chart_labels_json = '[]'
    monthly_chart_values_json = '[]'
    if request.user.is_authenticated and request.user.is_superuser:
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
        monthly_chart_labels_json = json.dumps([row['label'] for row in monthly_chart], ensure_ascii=False)
        monthly_chart_values_json = json.dumps([row['value'] for row in monthly_chart])
    return render(
        request,
        'catalog/home.html',
        page_context(
            latest_article=latest_article,
            latest_product=latest_product,
            stats=stats,
            monthly_chart=monthly_chart,
            monthly_chart_labels_json=monthly_chart_labels_json,
            monthly_chart_values_json=monthly_chart_values_json,
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
@login_required
def stats(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    # Aggregates
    revenue = Sale.objects.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    avg_sale = Sale.objects.aggregate(avg=Avg('total_amount'))['avg'] or Decimal('0.00')

    # Top and least popular products
    top_products = (
        SaleItem.objects.values('product__name')
        .annotate(total_qty=Sum('quantity'))
        .order_by('-total_qty', 'product__name')[:10]
    )
    # Products with zero sales
    products_qty = (
        Product.objects.annotate(qty=Coalesce(Sum('sale_items__quantity'), 0)).values('id', 'name', 'qty')
    )
    least_popular = [p for p in products_qty if p['qty'] == 0][:10]

    # Clients by city
    clients_by_city = Client.objects.values('city').annotate(count=Count('id')).order_by('-count')

    # Price list by product type
    price_list = {}
    for p in Product.objects.select_related('product_type').order_by('product_type__name', 'name'):
        key = p.product_type.name if p.product_type else '—'
        price_list.setdefault(key, []).append({'name': p.name, 'price': p.price})

    # Monthly sales totals
    monthly_sales_qs = (
        Sale.objects.annotate(month=TruncMonth('sale_date'))
        .values('month')
        .annotate(total=Sum('total_amount'))
        .order_by('month')
    )
    months = [row['month'] for row in monthly_sales_qs]
    month_labels = [timezone.localtime(m).strftime('%m/%Y') if m else '—' for m in months]
    month_values = [float(row['total'] or Decimal('0.00')) for row in monthly_sales_qs]

    # Monthly sales by product type
    monthly_by_type_qs = (
        SaleItem.objects.annotate(month=TruncMonth('sale__sale_date'), type=F('product__product_type__name'))
        .values('month', 'type')
        .annotate(total_qty=Sum('quantity'))
        .order_by('month', 'type')
    )
    # Build a mapping: {type: {month_label: qty}}
    types = set()
    monthly_by_type = {}
    for row in monthly_by_type_qs:
        t = row['type'] or '—'
        types.add(t)
        label = timezone.localtime(row['month']).strftime('%m/%Y') if row['month'] else '—'
        monthly_by_type.setdefault(t, {})[label] = row['total_qty']
    types = sorted(types)

    # Yearly receipts
    yearly_qs = (
        Sale.objects.annotate(year=TruncYear('sale_date')).values('year').annotate(total=Sum('total_amount')).order_by('year')
    )
    years = [row['year'] for row in yearly_qs]
    year_labels = [y.year for y in years]
    year_values = [float(row['total'] or Decimal('0.00')) for row in yearly_qs]

    # Helper: render matplotlib fig to base64 data uri
    def fig_to_datauri(fig):
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        data = base64.b64encode(buf.read()).decode('ascii')
        return f'data:image/png;base64,{data}'

    # Monthly totals plot (with linear trend and 3-month forecast)
    monthly_plot_uri = None
    if month_labels:
        fig, ax = plt.subplots(figsize=(8, 3))
        xs = list(range(len(month_values)))
        ys = month_values
        ax.plot(month_labels, ys, marker='o', label='Факт')
        # Linear regression
        n = len(xs)
        sum_x = sum(xs)
        sum_y = sum(ys)
        sum_x2 = sum(x * x for x in xs)
        sum_xy = sum(x * y for x, y in zip(xs, ys))
        denom = n * sum_x2 - sum_x * sum_x
        if denom != 0:
            slope = (n * sum_xy - sum_x * sum_y) / denom
            intercept = (sum_y - slope * sum_x) / n
            fit = [intercept + slope * x for x in xs]
            ax.plot(month_labels, fit, linestyle='--', color='orange', label='Тренд')
            # forecast next 3 months
            fx = [n + i for i in range(3)]
            f_labels = []
            last_month = months[-1]
            import datetime
            for i in range(1, 4):
                # add months
                year = last_month.year + (last_month.month + i - 1) // 12
                month = (last_month.month + i - 1) % 12 + 1
                f_labels.append(f'{month:02d}/{year}')
            f_values = [intercept + slope * x for x in fx]
            ax.plot(f_labels, f_values, linestyle=':', marker='x', color='green', label='Прогноз')
        ax.set_title('Месячная выручка')
        ax.set_ylabel('Сумма')
        ax.legend()
        monthly_plot_uri = fig_to_datauri(fig)

    # Monthly by type plot
    monthly_by_type_uri = None
    if month_labels and types:
        fig, ax = plt.subplots(figsize=(8, 4))
        for t in types:
            series = [monthly_by_type.get(t, {}).get(lbl, 0) for lbl in month_labels]
            ax.plot(month_labels, series, marker='o', label=t)
        ax.set_title('Месячные продажи по типам (шт)')
        ax.set_ylabel('Количество')
        ax.legend()
        monthly_by_type_uri = fig_to_datauri(fig)

    # Yearly receipts plot
    yearly_plot_uri = None
    if year_labels:
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.bar([str(y) for y in year_labels], year_values, color='#4a86e8')
        ax.set_title('Годовой отчёт поступлений')
        ax.set_ylabel('Сумма')
        yearly_plot_uri = fig_to_datauri(fig)

    # Clients by city plot
    clients_by_city_uri = None
    if clients_by_city:
        fig, ax = plt.subplots(figsize=(6, 3))
        labels = [row['city'] for row in clients_by_city]
        vals = [row['count'] for row in clients_by_city]
        ax.bar(labels, vals, color='#6aa84f')
        ax.set_title('Клиенты по городам')
        ax.set_ylabel('Число клиентов')
        clients_by_city_uri = fig_to_datauri(fig)

    return render(
        request,
        'catalog/stats.html',
        page_context(
            revenue=revenue,
            avg_sale=avg_sale,
            top_products=top_products,
            least_popular=least_popular,
            clients_by_city=clients_by_city,
            price_list=price_list,
            monthly_labels=month_labels,
            monthly_values=month_values,
            monthly_plot_uri=monthly_plot_uri,
            monthly_by_type_uri=monthly_by_type_uri,
            yearly_plot_uri=yearly_plot_uri,
            clients_by_city_uri=clients_by_city_uri,
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
    if not can_manage_model(request.user, model_key):
        raise PermissionDenied
    objects = spec['model'].objects.all()
    return render(request, 'catalog/generic_list.html', page_context(model_key=model_key, title=spec['title'], objects=objects, can_manage=True))
@login_required
@user_passes_test(is_staff_user)
def model_create(request, model_key):
    spec = get_spec(model_key)
    if not can_manage_model(request.user, model_key):
        raise PermissionDenied
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
    if not can_manage_model(request.user, model_key):
        raise PermissionDenied
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
    if not can_manage_model(request.user, model_key):
        raise PermissionDenied
    obj = get_object_or_404(spec['model'], pk=pk)
    if request.method == 'POST':
        logger.info('Удалён объект %s: %s', model_key, obj)
        obj.delete()
        messages.success(request, 'Объект удалён.')
        return redirect('catalog:model_list', model_key=model_key)
    return render(request, 'catalog/confirm_delete.html', page_context(object=obj, title=f'Удалить: {obj}'))
