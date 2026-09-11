from django.db import migrations, models


NEWS = [
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


def update_demo_news(apps, schema_editor):
    NewsArticle = apps.get_model('catalog', 'NewsArticle')
    for index, (title, summary, image_name) in enumerate(NEWS, start=1):
        article = NewsArticle.objects.filter(title=f'Новость {index}').first()
        if article:
            article.title = title
            article.summary = summary
            article.body = f'{summary} Материал подготовлен фабрикой «Добрая игрушка».'
            article.image = ''
            article.image_url = ''
            article.image_static_path = f'catalog/images/news/{image_name}-720.webp'
            article.save(update_fields=['title', 'summary', 'body', 'image', 'image_url', 'image_static_path'])


class Migration(migrations.Migration):
    dependencies = [('catalog', '0004_partner_companyinfo_certificate_text_and_more')]

    operations = [
        migrations.AddField(
            model_name='newsarticle',
            name='image_static_path',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.RunPython(update_demo_news, migrations.RunPython.noop),
    ]
