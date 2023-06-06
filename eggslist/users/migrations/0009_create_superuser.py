# Written manually by Fedor Grab on 2023-06-06 19:44

from django.conf import settings
from django.db import migrations


def generate_superuser(apps, schema_editor):
    User = apps.get_model("users.User")
    User.objects.create_superuser(
        email=settings.DJANGO_SUPERUSER_EMAIL,
        password=settings.DJANGO_SUPERUSER_PASSWORD,
    )

    print("\nInitial superuser created\n")

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_userstripeconnection'),
    ]

    operations = [
        migrations.RunPython(generate_superuser)
    ]
