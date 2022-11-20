# Generated by Django 4.0.2 on 2022-11-19 15:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0007_create_position_values'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_connection', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='transactions',
                                    to='users.userstripeconnection', verbose_name='stripe connection')),
                ('price', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='price')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='modified at')),
                ('status', models.CharField(choices=[('SU', 'Success'), ('FA', 'Failed'), ('PR', 'In progress'), ('CC', 'Checkout completed')], default='PR', max_length=2)),
                ('customer_email', models.CharField(max_length=256, null=True, verbose_name='customer_email')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='transactions', to='store.productarticle', verbose_name='product')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='seller_transactions', to=settings.AUTH_USER_MODEL, verbose_name='seller')),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                    related_name='customer_transactions', to=settings.AUTH_USER_MODEL,
                                    verbose_name='customer')),
            ],
        ),
    ]
