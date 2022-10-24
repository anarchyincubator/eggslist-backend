from django.db import migrations


def reorder(apps, schema_editor):
    Category = apps.get_model("store", "Category")

    for order, item in enumerate(Category.objects.all(), 1):
        item.position = order
        item.save(update_fields=["position"])


class Migration(migrations.Migration):
    dependencies = [("store", "0006_alter_category_options_category_position")]
    operations = [
        migrations.RunPython(reorder, reverse_code=migrations.RunPython.noop),
    ]
