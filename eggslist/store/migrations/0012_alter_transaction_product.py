# Generated by Django 4.0.2 on 2024-03-06 19:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_salestatistic_productarticle_is_archived'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transactions', to='store.productarticle', verbose_name='product'),
        ),
    ]
