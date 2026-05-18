from datetime import timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .forms import RegistrationForm
from .services import fetch_external_api_results, fetch_currency_rates, fetch_minsk_weather
from .models import Client as ToyClient, ContactPerson, Employee, NewsArticle, Product, ProductType, PromoCode, Review, Sale, SaleItem, Tag, ToyModel
from unittest.mock import Mock, patch
def adult_birth_date(years=25):
    return timezone.localdate() - timedelta(days=365 * years)
class CoreDomainTests(TestCase):
    def setUp(self):
        self.product_type = ProductType.objects.create(name='Плюшевые', description='Плюшевые игрушки')
        self.toy_model = ToyModel.objects.create(name='Модель A', description='Первая модель')
        self.tag = Tag.objects.create(name='мягкий')
        self.product_1 = Product.objects.create(code='TOY-001', name='Медведь', product_type=self.product_type, toy_model=self.toy_model, price=Decimal('15.00'))
        self.product_1.tags.add(self.tag)
        self.product_2 = Product.objects.create(code='TOY-002', name='Кубики', product_type=self.product_type, toy_model=self.toy_model, price=Decimal('25.00'))
        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'pass12345')
        self.employee_user = User.objects.create_user('employee', password='pass12345', is_staff=True)
        self.client_user = User.objects.create_user('client', password='pass12345')
        self.employee = Employee.objects.create(user=self.employee_user, full_name='Анна Иванова', phone='+375 (29) 222-33-44', position='Менеджер', specialization='Продажи', birth_date=adult_birth_date(30))
        self.client_profile = ToyClient.objects.create(user=self.client_user, full_name='Иван Петров', phone='+375 (29) 111-22-33', city='Минск', address='ул. Примерная, 1', birth_date=adult_birth_date(28))
        self.article = NewsArticle.objects.create(title='Новость 1', summary='Краткое содержание', body='Полный текст', is_published=True)
        ContactPerson.objects.create(full_name='Мария Ковалёва', role='Менеджер', phone='+375 (29) 333-44-55', email='maria@example.com')
    def test_client_age_validation(self):
        user = User.objects.create_user('young', password='pass12345')
        client = ToyClient(user=user, full_name='Молодой Клиент', phone='+375 (29) 333-44-55', city='Минск', address='Адрес', birth_date=timezone.localdate() - timedelta(days=17 * 365))
        with self.assertRaises(ValidationError):
            client.full_clean()
    def test_registration_form_requires_adult(self):
        form = RegistrationForm(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'ComplexPass123',
            'password2': 'ComplexPass123',
            'full_name': 'Новый Клиент',
            'phone': '+375 (29) 444-55-66',
            'city': 'Минск',
            'address': 'Улица 2',
            'birth_date': adult_birth_date(20),
        })
        self.assertTrue(form.is_valid())
    def test_home_shows_latest_article(self):
        response = self.client.get(reverse('catalog:home'))
        self.assertContains(response, 'Последняя опубликованная статья')
        self.assertContains(response, 'Новость 1')
    def test_news_pages_work(self):
        response = self.client.get(reverse('catalog:news'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Новость 1')
        detail = self.client.get(reverse('catalog:news_detail', args=[self.article.pk]))
        self.assertContains(detail, 'Полный текст')
    def test_public_pages_work(self):
        for name in ['catalog:about', 'catalog:glossary', 'catalog:contacts', 'catalog:privacy', 'catalog:vacancies', 'catalog:reviews', 'catalog:promo_codes']:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200)
    def test_reviews_can_be_added_by_logged_in_user(self):
        self.client.force_login(self.client_user)
        response = self.client.post(reverse('catalog:reviews'), {'rating': 5, 'text': 'Отлично!'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Review.objects.count(), 1)
    def test_api_demo_is_public(self):
        response = self.client.get(reverse('catalog:api_demo'))
        self.assertEqual(response.status_code, 200)
        summary = self.client.get(reverse('catalog:api_summary'))
        self.assertEqual(summary.status_code, 302)
    @patch('catalog.services.requests.get')
    def test_parallel_api_helper_returns_results(self, mocked_get):
        ok_response = Mock()
        ok_response.raise_for_status.return_value = None
        ok_response.json.return_value = {'result': 'ok'}
        mocked_get.return_value = ok_response
        results = fetch_external_api_results([
            ('First', 'https://example.com/first'),
            ('Second', 'https://example.com/second'),
        ])
        self.assertEqual(len(results), 2)
        self.assertTrue(all(item['ok'] for item in results))
        self.assertEqual(mocked_get.call_count, 2)

    @patch('catalog.services.requests.get')
    def test_currency_rates_helper(self, mocked_get):
        def side_effect(url, timeout=4):
            response = Mock()
            response.raise_for_status.return_value = None
            if 'USD' in url:
                response.json.return_value = {'Cur_Name': 'Доллар США', 'Cur_Scale': 1, 'Cur_OfficialRate': 3.25, 'Date': '2026-05-18T00:00:00'}
            elif 'EUR' in url:
                response.json.return_value = {'Cur_Name': 'Евро', 'Cur_Scale': 1, 'Cur_OfficialRate': 3.55, 'Date': '2026-05-18T00:00:00'}
            else:
                response.json.return_value = {'Cur_Name': 'Российский рубль', 'Cur_Scale': 100, 'Cur_OfficialRate': 3.4, 'Date': '2026-05-18T00:00:00'}
            return response

        mocked_get.side_effect = side_effect
        rates = fetch_currency_rates()
        self.assertEqual(len(rates), 3)
        self.assertEqual(rates[0]['code'], 'USD')
        self.assertEqual(rates[0]['byn_per_unit'], '3.2500')

    @patch('catalog.services.requests.get')
    def test_minsk_weather_helper(self, mocked_get):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {'current_weather': {'temperature': 18.5, 'windspeed': 4.1, 'winddirection': 120, 'weathercode': 1, 'time': '2026-05-18T12:00'}}
        mocked_get.return_value = response
        weather = fetch_minsk_weather()
        self.assertEqual(weather['temperature'], 18.5)
        self.assertEqual(weather['windspeed'], 4.1)

    @patch('catalog.views.fetch_currency_rates')
    @patch('catalog.views.fetch_minsk_weather')
    def test_api_demo_success(self, mocked_weather, mocked_rates):
        mocked_rates.return_value = [
            {'code': 'USD', 'name': 'Доллар США', 'scale': 1, 'byn_per_unit': '3.2500', 'date': '2026-05-18'},
        ]
        mocked_weather.return_value = {
            'temperature': 18.5,
            'windspeed': 4.1,
            'winddirection': 120,
            'weathercode': 1,
            'time': '2026-05-18T12:00',
        }
        response = self.client.get(reverse('catalog:api_demo'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Курсы валют к BYN')
        self.assertContains(response, 'Погода в Минске')
        mocked_rates.assert_called_once()
        mocked_weather.assert_called_once()
    def test_register_view_creates_client(self):
        response = self.client.post(reverse('catalog:register'), {
            'username': 'newclient',
            'email': 'newclient@example.com',
            'password1': 'ComplexPass123',
            'password2': 'ComplexPass123',
            'full_name': 'Новый Клиент',
            'phone': '+375 (29) 777-88-99',
            'city': 'Минск',
            'address': 'Улица 3',
            'birth_date': adult_birth_date(25),
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='newclient').exists())
        self.assertTrue(ToyClient.objects.filter(user__username='newclient').exists())
    def test_dashboard_for_staff_shows_all_sales(self):
        sale = Sale.objects.create(client=self.client_profile, employee=self.employee)
        SaleItem.objects.create(sale=sale, product=self.product_2, quantity=1, unit_price=self.product_2.price)
        self.client.force_login(self.employee_user)
        response = self.client.get(reverse('catalog:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Кабинет')
        self.assertContains(response, 'Кубики')
    def test_superuser_crud_views_work(self):
        self.client.force_login(self.superuser)
        list_response = self.client.get(reverse('catalog:model_list', args=['product-types']))
        self.assertEqual(list_response.status_code, 200)
        create_response = self.client.post(reverse('catalog:model_create', args=['product-types']), {
            'name': 'Развивающие',
            'description': 'Развивающие игрушки',
        }, follow=True)
        self.assertEqual(create_response.status_code, 200)
        created = ProductType.objects.get(name='Развивающие')
        update_response = self.client.post(reverse('catalog:model_update', args=['product-types', created.pk]), {
            'name': 'Развивающие обновлённые',
            'description': 'Обновлённое описание',
        }, follow=True)
        self.assertEqual(update_response.status_code, 200)
        self.assertTrue(ProductType.objects.filter(name='Развивающие обновлённые').exists())
        delete_response = self.client.post(reverse('catalog:model_delete', args=['product-types', created.pk]), follow=True)
        self.assertEqual(delete_response.status_code, 200)
        self.assertFalse(ProductType.objects.filter(pk=created.pk).exists())

    def test_staff_cannot_manage_product_types(self):
        self.client.force_login(self.employee_user)
        self.assertEqual(self.client.get(reverse('catalog:model_list', args=['product-types'])).status_code, 403)
        self.assertEqual(self.client.post(reverse('catalog:model_create', args=['product-types']), {'name': 'Тест', 'description': 'Тест'}).status_code, 403)

    def test_stats_page_requires_superuser(self):
        self.client.force_login(self.client_user)
        self.assertEqual(self.client.get(reverse('catalog:stats')).status_code, 403)
        self.client.force_login(self.superuser)
        response = self.client.get(reverse('catalog:stats'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Статистика')
        self.assertContains(response, 'Выручка')
    def test_product_search_and_sort(self):
        response = self.client.get(reverse('catalog:products'), {'q': 'Куб', 'sort': '-price'})
        self.assertContains(response, 'Кубики')
        self.assertNotContains(response, 'Медведь', status_code=200)
        products = list(response.context['products'])
        self.assertEqual(products[0].name, 'Кубики')
    def test_purchase_flow_creates_sale_and_total(self):
        self.client.force_login(self.client_user)
        response = self.client.post(reverse('catalog:product_detail', args=[self.product_1.pk]), {'quantity': 3}, follow=True)
        self.assertEqual(response.status_code, 200)
        sale = Sale.objects.get()
        item = sale.items.get()
        self.assertEqual(item.quantity, 3)
        self.assertEqual(item.unit_price, self.product_1.price)
        self.assertEqual(sale.total_amount, Decimal('45.00'))
    def test_purchase_flow_with_promo_code_applies_discount(self):
        PromoCode.objects.create(code='TOY20', description='Скидка 20%', discount_percent=20, is_active=True)
        self.client.force_login(self.client_user)
        response = self.client.post(reverse('catalog:product_detail', args=[self.product_1.pk]), {'quantity': 5, 'promo_code': 'TOY20'}, follow=True)
        self.assertEqual(response.status_code, 200)
        sale = Sale.objects.get()
        self.assertEqual(sale.discount_percent, 20)
        self.assertEqual(sale.total_amount, Decimal('60.00'))
        self.assertEqual(sale.promo_code.code, 'TOY20')
    def test_product_list_is_paginated(self):
        for idx in range(3, 10):
            Product.objects.create(code=f'TOY-{idx:03d}', name=f'Игрушка {idx}', product_type=self.product_type, toy_model=self.toy_model, price=Decimal('10.00') + Decimal(idx))
        response = self.client.get(reverse('catalog:products'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['page_obj'].has_next())
    def test_news_list_is_paginated(self):
        for idx in range(2, 9):
            NewsArticle.objects.create(title=f'Новость {idx}', summary=f'Краткое содержание {idx}', body='Полный текст', is_published=True, published_at=timezone.now() - timedelta(days=idx))
        response = self.client.get(reverse('catalog:news'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['page_obj'].has_next())
    def test_dashboard_for_client_shows_own_sales(self):
        sale = Sale.objects.create(client=self.client_profile, employee=self.employee)
        SaleItem.objects.create(sale=sale, product=self.product_2, quantity=2, unit_price=self.product_2.price)
        self.client.force_login(self.client_user)
        response = self.client.get(reverse('catalog:dashboard'))
        self.assertContains(response, 'Кабинет')
        self.assertContains(response, 'Кубики')
    def test_home_hides_stats_for_regular_users(self):
        sale = Sale.objects.create(client=self.client_profile, employee=self.employee)
        SaleItem.objects.create(sale=sale, product=self.product_2, quantity=1, unit_price=self.product_2.price)
        self.client.force_login(self.client_user)
        response = self.client.get(reverse('catalog:home'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Краткая статистика')
        self.assertNotContains(response, 'График выручки по месяцам')

    def test_home_hides_stats_for_anonymous_users(self):
        sale = Sale.objects.create(client=self.client_profile, employee=self.employee)
        SaleItem.objects.create(sale=sale, product=self.product_2, quantity=1, unit_price=self.product_2.price)
        response = self.client.get(reverse('catalog:home'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Краткая статистика')
        self.assertNotContains(response, 'График выручки по месяцам')

    def test_stats_page_redirects_anonymous_users(self):
        response = self.client.get(reverse('catalog:stats'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_home_shows_stats_for_superuser(self):
        sale = Sale.objects.create(client=self.client_profile, employee=self.employee)
        SaleItem.objects.create(sale=sale, product=self.product_2, quantity=1, unit_price=self.product_2.price)
        self.client.force_login(self.superuser)
        response = self.client.get(reverse('catalog:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Краткая статистика')
        self.assertContains(response, 'График выручки по месяцам')
    def test_product_detail_by_code_route(self):
        response = self.client.get(reverse('catalog:product_detail_by_code', args=['TOY-001']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Медведь')
    def test_logout_via_post_redirects_home(self):
        self.client.force_login(self.client_user)
        response = self.client.post(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Фабрика игрушек')

    # --- API tests ---
    def test_api_products_list_and_detail(self):
        response = self.client.get(reverse('catalog:api_products_list'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('items', data)
        first = data['items'][0]
        detail = self.client.get(reverse('catalog:api_product_detail', args=[first['id']]))
        self.assertEqual(detail.status_code, 200)
        det = detail.json()
        self.assertEqual(det['id'], first['id'])

    def test_api_purchase_requires_client(self):
        # anonymous should be redirected to login
        response = self.client.post(reverse('catalog:api_purchase'), {'product': self.product_1.pk, 'quantity': 1})
        self.assertEqual(response.status_code, 302)
        # client user can purchase
        self.client.force_login(self.client_user)
        response = self.client.post(reverse('catalog:api_purchase'), {'product': self.product_1.pk, 'quantity': 2})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('sale_id', data)

    def test_api_clients_by_city_requires_staff(self):
        # regular client forbidden
        self.client.force_login(self.client_user)
        resp = self.client.get(reverse('catalog:api_clients_by_city'))
        self.assertEqual(resp.status_code, 403)
        # staff allowed
        self.client.force_login(self.employee_user)
        resp = self.client.get(reverse('catalog:api_clients_by_city'))
        self.assertEqual(resp.status_code, 200)

    def test_api_employee_sales_for_employee(self):
        # create a sale assigned to employee
        sale = Sale.objects.create(client=self.client_profile, employee=self.employee)
        SaleItem.objects.create(sale=sale, product=self.product_2, quantity=3, unit_price=self.product_2.price)
        # non-employee cannot access
        self.client.force_login(self.client_user)
        resp = self.client.get(reverse('catalog:api_employee_sales'))
        self.assertEqual(resp.status_code, 403)
        # employee can access
        self.client.force_login(self.employee_user)
        resp = self.client.get(reverse('catalog:api_employee_sales'))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('sales', data)

