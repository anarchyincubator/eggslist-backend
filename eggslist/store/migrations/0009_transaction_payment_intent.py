# Generated by Django 4.0.2 on 2022-11-22 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_transaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='payment_intent',
            field=models.CharField(default=None, max_length=80, null=True, verbose_name='payment intent'),
        ),
    ]
