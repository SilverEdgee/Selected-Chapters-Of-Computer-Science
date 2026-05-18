# Финальный чеклист соответствия требованиям Лр5 Django

Дата проверки: 2026-05-18

## Обозначения
- ✅ Выполнено
- 🟡 Частично
- ❌ Не реализовано

## Чеклист

1. ✅ Определены сущности предметной области и реализованы модели со связями OneToOne / ForeignKey / ManyToMany
   - Файл: `catalog/models.py`
   - Модели: `ProductType`, `ToyModel`, `Tag`, `Product`, `Client`, `Employee`, `Sale`, `SaleItem`, `CompanyInfo`, `NewsArticle`, `FAQEntry`, `ContactPerson`, `Vacancy`, `Review`, `PromoCode`

2. ✅ Главная страница с краткой информацией о последней опубликованной статье
   - Файлы: `catalog/views.py`, `templates/catalog/home.html`

3. ✅ Страница «О компании» с данными из базы
   - Файлы: `catalog/models.py`, `catalog/views.py`, `templates/catalog/about.html`

4. ✅ Страница «Новости» со списком статей, кратким содержанием и переходом к полной статье
   - Файлы: `catalog/models.py`, `catalog/views.py`, `templates/catalog/news_list.html`, `templates/catalog/news_detail.html`

5. ✅ Страница «Словарь терминов и понятий» / FAQ
   - Файлы: `catalog/models.py`, `catalog/views.py`, `templates/catalog/glossary.html`

6. ✅ Страница «Контакты» с сотрудниками, телефонами и почтой
   - Файлы: `catalog/models.py`, `catalog/views.py`, `templates/catalog/contacts.html`

7. ✅ Страница «Политика конфиденциальности»
   - Файлы: `catalog/views.py`, `templates/catalog/privacy.html`

8. ✅ Страница «Вакансии»
   - Файлы: `catalog/models.py`, `catalog/views.py`, `templates/catalog/vacancies.html`

9. ✅ Страница «Отзывы» с возможностью добавления отзыва авторизованным пользователем
   - Файлы: `catalog/models.py`, `catalog/forms.py`, `catalog/views.py`, `templates/catalog/reviews.html`

10. ✅ Страница «Промокоды и купоны» со списком действующих и архивных промокодов
    - Файлы: `catalog/models.py`, `catalog/views.py`, `templates/catalog/promo_codes.html`

11. ✅ Реализованы связи OneToOneField, ForeignKey и ManyToManyField
    - Файл: `catalog/models.py`

12. ✅ Реализованы CRUD-операции
    - Файлы: `catalog/views.py`, `catalog/urls.py`, `templates/catalog/generic_list.html`, `templates/catalog/form.html`, `templates/catalog/confirm_delete.html`

13. ✅ Все модели добавлены в админ-панель; есть inline-редактирование связанных записей
    - Файлы: `catalog/admin.py`, `catalog/management/commands/seed_demo_data.py`

14. ✅ Реализованы механизмы авторизации и аутентификации
    - Файлы: `toy_factory_site/urls.py`, `catalog/views.py`, `templates/registration/login.html`, `templates/catalog/base.html`

15. ✅ Разграничение доступа: superuser/staff и зарегистрированный пользователь
    - Файлы: `catalog/views.py`, `templates/catalog/base.html`

16. ✅ Есть демонстрационные данные не менее 10 записей
    - Файл: `catalog/management/commands/seed_demo_data.py`

17. ✅ Подключены и используются минимум 2 сторонних API
    - Файл: `catalog/views.py` (`api_demo`, `api_summary`)

18. ✅ Используются регулярные выражения в URL-маршрутах
    - Файл: `catalog/urls.py`

19. ✅ Отображаются статистические показатели сайта
    - Файлы: `catalog/views.py`, `templates/catalog/stats.html`, `templates/catalog/home.html`

20. ✅ Отображаются текущая дата, UTC, таймзона пользователя и даты в форматах DD/MM/YYYY
    - Файлы: `templates/catalog/base.html`, `templates/catalog/home.html`, `templates/catalog/news_list.html`, `templates/catalog/news_detail.html`, `templates/catalog/stats.html`

21. ✅ Телефон клиента в формате `+375 (29) XXX-XX-XX`
    - Файлы: `catalog/models.py`, `catalog/forms.py`

22. ✅ Клиенты и сотрудники имеют возрастное ограничение 18+
    - Файлы: `catalog/models.py`, `catalog/forms.py`

23. ✅ Реализована визуализация графиков/диаграмм
    - Файлы: `catalog/views.py`, `templates/catalog/home.html`, `templates/catalog/stats.html`

24. ✅ Реализованы поиск и сортировка данных
    - Файлы: `catalog/views.py`, `templates/catalog/product_list.html`

25. ✅ Добавлены тесты
    - Файл: `catalog/tests.py`

26. ✅ Покрытие тестами 80% и выше
    - Файлы: `catalog/tests.py` + отчёт coverage
    - Итог: общий coverage **93%**

27. ✅ Добавлено logging
    - Файл: `catalog/views.py`
    - Настройка: `toy_factory_site/settings.py`

28. ✅ Внешний вид сайта не критичен, нужная информация отображается
    - Файлы: шаблоны `templates/catalog/*.html`

29. ✅ Серверная и клиентская валидация форм
    - Файлы: `catalog/forms.py`, `catalog/models.py`, `templates/catalog/form.html`

30. ✅ Поддержка разных уровней логирования из конфигурации
    - Файл: `toy_factory_site/settings.py`

31. ✅ Ограничено использование API для неавторизованных пользователей
    - Файлы: `catalog/views.py`, `toy_factory_site/urls.py`

32. ✅ Дополнительное задание: параллельный код
    - Файлы: `catalog/services.py`, `catalog/views.py`

33. ✅ Дополнительное задание: production API
    - Файлы: `Dockerfile`, `docker-compose.yml`, `requirements.txt`
    - Запуск через `gunicorn`

34. ✅ Дополнительное задание: Dockerfile
    - Файл: `Dockerfile`

35. ✅ Дополнительное задание: docker-compose
    - Файл: `docker-compose.yml`

36. 🟡 Дополнительное задание: развертывание в облаке
    - Статус: отдельно не разворачивалось, но проект уже готов к контейнеризации

## Дополнительные улучшения, которые уже добавлены
- ✅ Покупка теперь создаётся атомарно
- ✅ Промокод может применяться к покупке
- ✅ Добавлена пагинация товаров и новостей
- ✅ Добавлена загрузка файлов для новостей и контактов
- ✅ Добавлены интерактивные графики на главной и в статистике
- ✅ Параллельная загрузка внешних API
- ✅ Docker-сборка и запуск через compose

## Проверка
- `python -m py_compile` для изменённых файлов — без ошибок
- `pytest -q` — 21 passed
- `coverage run -m pytest` / `coverage report -m` — общий coverage 93%



