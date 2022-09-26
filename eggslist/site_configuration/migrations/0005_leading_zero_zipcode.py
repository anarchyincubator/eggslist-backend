from django.db import migrations
from django.db.models import CharField, F, Value
from django.db.models.functions import Concat, Length


def add_leading_zero(apps, schema_editor):
    LocationZipCode = apps.get_model("site_configuration", "LocationZipCode")
    db_alias = schema_editor.connection.alias
    qs = (
        LocationZipCode.objects.using(db_alias)
        .annotate(name_length=Length("name"))
        .filter(name_length__lte=4)
    )
    qs.update(name=Concat(Value("0"), F("name"), output_field=CharField()))


class Migration(migrations.Migration):
    dependencies = [("site_configuration", "0004_teammember")]
    operations = [migrations.RunPython(add_leading_zero, migrations.RunPython.noop)]
