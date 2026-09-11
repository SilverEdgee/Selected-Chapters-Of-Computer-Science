from django.db import migrations, models


def add_demo_certificate(apps, schema_editor):
    CompanyInfo = apps.get_model('catalog', 'CompanyInfo')
    CompanyInfo.objects.filter(certificate_image_static_path='').update(
        certificate_image_static_path='catalog/images/certificate-demo-720.webp'
    )


class Migration(migrations.Migration):
    dependencies = [('catalog', '0005_news_images_and_demo_content')]
    operations = [
        migrations.AddField(
            model_name='companyinfo',
            name='certificate_image',
            field=models.FileField(blank=True, null=True, upload_to='company/certificates/'),
        ),
        migrations.AddField(
            model_name='companyinfo',
            name='certificate_image_static_path',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.RunPython(add_demo_certificate, migrations.RunPython.noop),
    ]
