# Generated by Django 4.0.2 on 2022-09-12 01:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_user_is_verified_seller_pending'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='verifiedsellerapplication',
            options={'ordering': ('status',), 'verbose_name': 'verified seller application', 'verbose_name_plural': 'verified seller application'},
        ),
        migrations.AddField(
            model_name='verifiedsellerapplication',
            name='status',
            field=models.IntegerField(choices=[(0, 'pending'), (1, 'approved'), (2, 'refused')], default=0, verbose_name='status'),
        ),
        migrations.AlterField(
            model_name='verifiedsellerapplication',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
    ]
