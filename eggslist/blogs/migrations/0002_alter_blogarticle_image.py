# Generated by Django 4.0.2 on 2022-07-20 17:58

import imagekit.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogarticle',
            name='image',
            field=imagekit.models.fields.ProcessedImageField(blank=True, null=True, upload_to='blogs'),
        ),
    ]
