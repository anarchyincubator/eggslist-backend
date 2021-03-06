# Generated by Django 4.0.2 on 2022-07-20 17:58

import imagekit.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productarticle',
            options={'ordering': ('-engagement_count',), 'verbose_name': 'product article', 'verbose_name_plural': 'product articles'},
        ),
        migrations.AlterField(
            model_name='category',
            name='image',
            field=imagekit.models.fields.ProcessedImageField(upload_to='categories'),
        ),
        migrations.AlterField(
            model_name='productarticle',
            name='image',
            field=imagekit.models.fields.ProcessedImageField(blank=True, null=True, upload_to='product_articles'),
        ),
    ]
