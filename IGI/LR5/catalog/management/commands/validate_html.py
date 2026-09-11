from html.parser import HTMLParser

from django.core.management.base import BaseCommand
from django.test import Client
from django.urls import reverse


VOID_ELEMENTS = {
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
    'link', 'meta', 'param', 'source', 'track', 'wbr',
}


class SemanticHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []
        self.ids = set()
        self.tags = {}
        self.has_description = False
        self.has_viewport = False
        self.has_lang = False
        self.has_microdata = False

    def handle_starttag(self, tag, attrs):
        self.tags[tag] = self.tags.get(tag, 0) + 1
        names = [name for name, _ in attrs]
        duplicates = sorted({name for name in names if names.count(name) > 1})
        if duplicates:
            self.errors.append(f'<{tag}>: повтор атрибутов {", ".join(duplicates)}')
        attributes = dict(attrs)
        element_id = attributes.get('id')
        if element_id:
            if element_id in self.ids:
                self.errors.append(f'повтор id="{element_id}"')
            self.ids.add(element_id)
        if tag == 'html':
            self.has_lang = bool(attributes.get('lang'))
        if tag == 'meta' and attributes.get('name') == 'description':
            self.has_description = bool(attributes.get('content'))
        if tag == 'meta' and attributes.get('name') == 'viewport':
            self.has_viewport = True
        if 'itemscope' in attributes or 'itemtype' in attributes:
            self.has_microdata = True
        if tag == 'img' and not attributes.get('alt'):
            self.errors.append('<img> без непустого alt')
        if tag == 'iframe' and not attributes.get('title'):
            self.errors.append('<iframe> без title')
        if tag not in VOID_ELEMENTS:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_ELEMENTS and self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag in VOID_ELEMENTS:
            self.errors.append(f'лишний закрывающий тег </{tag}>')
            return
        if not self.stack:
            self.errors.append(f'закрывающий тег </{tag}> без открывающего')
            return
        if self.stack[-1] != tag:
            self.errors.append(f'ожидался </{self.stack[-1]}>, получен </{tag}>')
            if tag in self.stack:
                while self.stack and self.stack[-1] != tag:
                    self.stack.pop()
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def validate(self):
        if self.stack:
            self.errors.append(f'незакрытые теги: {", ".join(self.stack)}')
        required = ['title', 'header', 'nav', 'main', 'footer', 'h1']
        for tag in required:
            if not self.tags.get(tag):
                self.errors.append(f'нет обязательного элемента <{tag}>')
        if self.tags.get('h1', 0) != 1:
            self.errors.append(f'ожидался один <h1>, найдено {self.tags.get("h1", 0)}')
        if not self.has_lang:
            self.errors.append('у <html> не задан lang')
        if not self.has_description:
            self.errors.append('не задан meta description')
        if not self.has_viewport:
            self.errors.append('не задан meta viewport')
        if not self.has_microdata:
            self.errors.append('не найдены атрибуты микроданных')
        return self.errors


class Command(BaseCommand):
    help = 'Локально проверяет структуру и семантические требования сгенерированных HTML-страниц.'

    def handle(self, *args, **options):
        client = Client()
        pages = {
            'Главная': reverse('catalog:home'),
            'Каталог': reverse('catalog:products'),
            'Подбор игрушки': f"{reverse('catalog:toy_selection')}?submit=1&budget=50",
            'О компании': reverse('catalog:about'),
            'Новости': reverse('catalog:news'),
            'Словарь': reverse('catalog:glossary'),
            'Контакты': reverse('catalog:contacts'),
            'Политика': reverse('catalog:privacy'),
            'Вакансии': reverse('catalog:vacancies'),
            'Отзывы': reverse('catalog:reviews'),
            'Промокоды': reverse('catalog:promo_codes'),
            'Корзина': reverse('catalog:cart'),
        }
        total_errors = 0
        for title, url in pages.items():
            response = client.get(url)
            if response.status_code != 200:
                self.stderr.write(self.style.ERROR(f'{title}: HTTP {response.status_code}'))
                total_errors += 1
                continue
            parser = SemanticHTMLParser()
            parser.feed(response.content.decode(response.charset or 'utf-8'))
            errors = parser.validate()
            if errors:
                total_errors += len(errors)
                self.stderr.write(self.style.ERROR(f'{title}: {len(errors)} ошибок'))
                for error in errors:
                    self.stderr.write(f'  - {error}')
            else:
                self.stdout.write(self.style.SUCCESS(f'{title}: OK'))
        if total_errors:
            raise SystemExit(f'Проверка завершилась с ошибками: {total_errors}')
        self.stdout.write(self.style.SUCCESS(f'Проверено страниц: {len(pages)}; ошибок: 0'))
