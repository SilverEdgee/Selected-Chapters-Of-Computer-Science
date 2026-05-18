from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_companyinfo_contactperson_faqentry_newsarticle_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='newsarticle',
            name='image',
            field=models.FileField(blank=True, null=True, upload_to='news/'),
        ),
        migrations.AddField(
            model_name='contactperson',
            name='photo',
            field=models.FileField(blank=True, null=True, upload_to='contacts/'),
        ),
        migrations.AddField(
            model_name='sale',
            name='discount_percent',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='sale',
            name='promo_code',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sales', to='catalog.promocode'),
        ),
    ]

