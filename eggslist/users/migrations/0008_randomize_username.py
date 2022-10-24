import secrets

from django.db import migrations


def randomize_username(apps, schema_editor):
    User = apps.get_model("users", "User")
    db_alias = schema_editor.connection.alias
    qs = User.objects.filter(is_staff=False)

    for user in qs:
        user.username = secrets.token_hex(8)
        user.save(using=db_alias)


class Migration(migrations.Migration):
    dependencies = [("users", "0007_alter_verifiedsellerapplication_options_and_more")]
    operations = [migrations.RunPython(randomize_username, migrations.RunPython.noop)]
