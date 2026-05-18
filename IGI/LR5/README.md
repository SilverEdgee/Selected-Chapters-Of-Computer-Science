# ЛР5 — Django, вариант 22
Минимально рабочий проект для варианта 22: **Фабрика игрушек**.
## Что есть
- варианты и общие страницы из задания: главная, о компании, новости, словарь, контакты, политика, вакансии, отзывы, промокоды
- модели: типы игрушек, модели, теги, товары, клиенты, сотрудники, продажи, позиции продаж, компания, новости, FAQ, контакты, вакансии, отзывы, промокоды
- связи OneToOne, ForeignKey, ManyToMany
- админка Django
- регистрация и вход
- CRUD для сущностей для staff/superuser
- поиск и сортировка товаров
- статистика и простая визуализация
- использование двух внешних API
- ограничение доступа к API для неавторизованных
- логирование
- тесты
- команда для демо-данных
## Запуск
```bash
cd /home/denchik/453503_Pometko_23/IGI/LR5
source .venv/bin/activate
python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver
```
Если удобнее, можно запускать через `main.py`:
```bash
python main.py runserver
```
## Доступы для демо
- admin / admin123
- employee / employee123
- client / client123
## Тесты
```bash
pytest
```

## Покрытие тестами
```bash
coverage run -m pytest
coverage report -m
```

## Docker
```bash
docker build -t lr5-toy-factory .
docker run --rm -p 8000:8000 lr5-toy-factory
```

Или через compose:
```bash
docker compose up --build
```

