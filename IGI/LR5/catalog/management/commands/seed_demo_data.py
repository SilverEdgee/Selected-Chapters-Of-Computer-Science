from datetime import timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone
from catalog.models import (
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
class Command(BaseCommand):
    help = 'Создаёт демонстрационные данные для варианта 22.'
    def handle(self, *args, **options):
        admin_user, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com'})
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.set_password('admin123')
        admin_user.save()
        employee_user, _ = User.objects.get_or_create(username='employee', defaults={'email': 'employee@example.com'})
        employee_user.is_staff = True
        employee_user.set_password('employee123')
        employee_user.save()
        client_user, _ = User.objects.get_or_create(username='client', defaults={'email': 'client@example.com'})
        client_user.set_password('client123')
        client_user.save()
        types = [ProductType.objects.get_or_create(name=name, defaults={'description': f'Описание категории {name}'})[0] for name in ['Плюшевые', 'Конструкторы', 'Настольные']]
        models = [ToyModel.objects.get_or_create(name=name, defaults={'description': name})[0] for name in ['Модель A', 'Модель B', 'Модель C', 'Модель D']]
        tags = [Tag.objects.get_or_create(name=name)[0] for name in ['образовательный', 'мягкий', 'коллекционный', 'яркий']]
        products = []
        for i in range(1, 11):
            product, _ = Product.objects.get_or_create(
                code=f'TOY-{i:03d}',
                defaults={
                    'name': f'Игрушка {i}',
                    'product_type': types[i % len(types)],
                    'toy_model': models[i % len(models)],
                    'price': Decimal('10.00') + Decimal(i) * Decimal('3.5'),
                    'description': f'Безопасная игрушка №{i} из прочных материалов для творчества и развития.',
                    'is_active': True,
                },
            )
            product.tags.set(tags[: (i % 4) + 1])
            products.append(product)
        client, _ = Client.objects.get_or_create(
            user=client_user,
            defaults={
                'full_name': 'Иван Петров',
                'phone': '+375 (29) 111-22-33',
                'city': 'Минск',
                'address': 'ул. Примерная, 1',
                'birth_date': timezone.localdate() - timedelta(days=30 * 365),
            },
        )
        employee, _ = Employee.objects.get_or_create(
            user=employee_user,
            defaults={
                'full_name': 'Анна Иванова',
                'phone': '+375 (29) 222-33-44',
                'position': 'Менеджер',
                'specialization': 'Продажи',
                'birth_date': timezone.localdate() - timedelta(days=32 * 365),
            },
        )
        company, _ = CompanyInfo.objects.get_or_create(
            title='Фабрика игрушек',
            defaults={
                'description': 'Компания занимается производством и продажей игрушек.',
                'mission': 'Обеспечивать детей качественными игрушками.',
                'requisites': 'Реквизиты компании для демонстрации.',
                'certificate_text': 'Сертификат соответствия BY/112 03.11. ТР008 00125 подтверждает безопасность демонстрационной продукции.',
                'certificate_image_static_path': 'catalog/images/certificate-demo-720.webp',
            },
        )
        if not company.certificate_text:
            company.certificate_text = 'Сертификат соответствия BY/112 03.11. ТР008 00125 подтверждает безопасность демонстрационной продукции.'
            company.save(update_fields=['certificate_text', 'updated_at'])
        if not company.certificate_image and not company.certificate_image_static_path:
            company.certificate_image_static_path = 'catalog/images/certificate-demo-720.webp'
            company.save(update_fields=['certificate_image_static_path', 'updated_at'])
        for year, title, description in [
            (2014, 'Открытие мастерской', 'Начали выпуск небольших серий деревянных игрушек.'),
            (2018, 'Собственная лаборатория', 'Организовали контроль материалов и качества каждой партии.'),
            (2022, 'Интернет-каталог', 'Открыли онлайн-заказ и доставку по Беларуси.'),
            (2026, 'Экологичная коллекция', 'Перешли на перерабатываемую упаковку для основной линейки.'),
        ]:
            CompanyMilestone.objects.get_or_create(
                company=company,
                year=year,
                defaults={'title': title, 'description': description},
            )
        for name, website, description, logo_path in [
            ('БелЛесИгрушка', 'https://www.bellesbumprom.by/', 'Поставщик сертифицированной древесины.', 'catalog/images/partner-forest.svg'),
            ('Добрая доставка', 'https://belpost.by/', 'Партнёр по доставке заказов.', 'catalog/images/partner-delivery.svg'),
            ('Мир детства', 'https://edu.gov.by/', 'Образовательный партнёр фабрики.', 'catalog/images/partner-education.svg'),
        ]:
            Partner.objects.get_or_create(
                name=name,
                defaults={
                    'website': website,
                    'description': description,
                    'logo_static_path': logo_path,
                    'is_active': True,
                },
            )
        news = [
            ('Новая коллекция деревянных игрушек', 'В мастерской завершена новая серия поездов, фигурок животных и строительных наборов.', 'new-collection'),
            ('Как фабрика проверяет качество игрушек', 'Каждая игрушка проходит проверку сборки, размеров деталей и безопасности покрытия.', 'quality-control'),
            ('Экологичные материалы в производстве', 'Для новых серий используются древесина, хлопковые ткани и перерабатываемая упаковка.', 'eco-materials'),
            ('Новая упаковка для доставки заказов', 'Игрушки теперь отправляются в прочных коробках с бумажным наполнителем.', 'order-packing'),
            ('Развивающие наборы для дошкольников', 'В каталог добавлены сортеры, пирамидки и наборы для изучения форм и цветов.', 'educational-toys'),
            ('Как дизайнеры создают новую игрушку', 'Показываем путь от первого эскиза до готового деревянного образца.', 'design-studio'),
            ('Мастерская расширила производство', 'Дополнительные рабочие места позволят выпускать больше деревянных игрушек.', 'new-collection'),
            ('Месяц усиленного контроля качества', 'Специалисты дополнительно проверяют крепления и качество обработки каждой партии.', 'quality-control'),
            ('Фабрика сокращает использование пластика', 'В упаковке заказов пластик постепенно заменяется бумагой и натуральными материалами.', 'eco-materials'),
            ('Игры, которые помогают развитию', 'Новая подборка знакомит детей с формами, цветами и построением простых конструкций.', 'educational-toys'),
        ]
        for idx, (title, summary, image_name) in enumerate(news, start=1):
            NewsArticle.objects.get_or_create(
                title=title,
                defaults={
                    'summary': summary,
                    'body': f'{summary} Материал подготовлен фабрикой «Добрая игрушка».',
                    'image_static_path': f'catalog/images/news/{image_name}-720.webp',
                    'published_at': timezone.now() - timedelta(days=idx * 3),
                    'is_published': True,
                },
            )
        for q, a in [
            ('Какие игрушки самые популярные?', 'Плюшевые и развивающие игрушки.'),
            ('Есть ли доставка?', 'Да, доставка доступна.'),
            ('Можно ли оставить отзыв?', 'Да, после входа в аккаунт.'),
            ('Как посмотреть статистику?', 'В разделе статистики.'),
            ('Где находятся контакты?', 'На отдельной странице контактов.'),
        ]:
            FAQEntry.objects.get_or_create(question=q, defaults={'answer': a})
        for name, role, phone, email in [
            ('Мария Ковалёва', 'Менеджер', '+375 (29) 333-44-55', 'maria@example.com'),
            ('Олег Смирнов', 'Логист', '+375 (29) 444-55-66', 'oleg@example.com'),
            ('Ирина Орлова', 'Маркетолог', '+375 (29) 555-66-77', 'irina@example.com'),
            ('Павел Новиков', 'Кладовщик', '+375 (29) 666-77-88', 'pavel@example.com'),
            ('Анна Лебедева', 'Бухгалтер', '+375 (29) 777-88-99', 'anna@example.com'),
            ('Дмитрий Кузнецов', 'Технолог', '+375 (29) 888-99-00', 'dmitry@example.com'),
            ('Елена Соколова', 'HR-специалист', '+375 (29) 111-22-33', 'elena@example.com'),
            ('Сергей Морозов', 'Дизайнер', '+375 (29) 222-33-44', 'sergey@example.com'),
            ('Наталья Волкова', 'Контролёр качества', '+375 (29) 333-55-77', 'natalia@example.com'),
            ('Виктор Зайцев', 'Инженер', '+375 (29) 444-66-88', 'viktor@example.com'),
        ]:
            ContactPerson.objects.get_or_create(full_name=name, defaults={'role': role, 'phone': phone, 'email': email, 'description': f'{role} компании.'})
        for title, salary in [
            ('Менеджер по продажам', 'от 1200 BYN'),
            ('Контент-менеджер', 'от 1100 BYN'),
            ('Складской работник', 'от 1000 BYN'),
        ]:
            Vacancy.objects.get_or_create(title=title, defaults={'description': f'Описание вакансии {title}.', 'salary': salary, 'is_active': True})
        Review.objects.get_or_create(user=client_user, name='Иван Петров', rating=5, defaults={'text': 'Отличный сервис!', 'is_approved': True})
        Review.objects.get_or_create(user=employee_user, name='Анна Иванова', rating=4, defaults={'text': 'Хороший ассортимент.', 'is_approved': True})
        Review.objects.get_or_create(name='Гость', rating=5, defaults={'text': 'Всё понравилось.', 'is_approved': True})
        for code, desc, pct, archived in [
            ('TOY10', 'Скидка 10%', 10, False),
            ('TOY15', 'Скидка 15%', 15, False),
            ('ARCH01', 'Архивный купон', 5, True),
            ('ARCH02', 'Архивный купон 2', 7, True),
        ]:
            PromoCode.objects.get_or_create(code=code, defaults={'description': desc, 'discount_percent': pct, 'is_active': not archived, 'is_archived': archived})
        if not Sale.objects.exists():
            for idx in range(1, 6):
                sale = Sale.objects.create(client=client, employee=employee, sale_date=timezone.now() - timedelta(days=idx * 10), notes=f'Демо-продажа {idx}')
                SaleItem.objects.create(sale=sale, product=products[idx], quantity=idx, unit_price=products[idx].price)
                SaleItem.objects.create(sale=sale, product=products[idx + 1], quantity=1, unit_price=products[idx + 1].price)
        self.stdout.write(self.style.SUCCESS('Демо-данные созданы.'))
