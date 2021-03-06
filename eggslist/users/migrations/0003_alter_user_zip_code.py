# Generated by Django 4.0.2 on 2022-07-20 17:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site_configuration', '0003_faq_testimonial'),
        ('users', '0002_alter_user_managers_user_is_email_verified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='zip_code',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='site_configuration.locationzipcode', verbose_name='zip code'),
        ),
    ]
