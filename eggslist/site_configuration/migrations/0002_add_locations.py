import pandas as pd
from django.conf import settings
from django.db import migrations
from django.utils.text import slugify


def create_locations(apps, schema_editor):
    Country = apps.get_model("site_configuration", "LocationCountry")
    Country.slug_field_name = "name"
    Country.slug_field_unique = True
    State = apps.get_model("site_configuration", "LocationState")
    State.slug_field_name = "name"
    State.slug_field_unique = True
    City = apps.get_model("site_configuration", "LocationCity")
    State.slug_field_name = "name"
    State.slug_field_uniqe = True
    ZipCode = apps.get_model("site_configuration", "LocationZipCode")
    ZipCode.slug_field_name = "name"
    ZipCode.slug_field_unique = True

    CITY_COLUMN = "city"
    STATE_COLUMN = "state_id"
    ZIP_COLUMN = "zip"
    db_alias = schema_editor.connection.alias

    us_geo_data = pd.read_csv(settings.GEO_ZIP_PATH)
    try:
        us_country = Country.objects.using(db_alias).get(name="United States")
    except Country.DoesNotExist:
        us_country = Country.objects.using(db_alias).create(name="United States")

    states = [
        State(name=state_name, country=us_country, slug=slugify(state_name))
        for state_name in us_geo_data[STATE_COLUMN].unique()
    ]
    State.objects.using(db_alias).bulk_create(states, ignore_conflicts=True)

    for state in State.objects.using(db_alias).all():
        cities = [
            City(state=state, name=city_name, slug=slugify(city_name))
            for city_name in us_geo_data[us_geo_data[STATE_COLUMN] == state.name][
                CITY_COLUMN
            ].unique()
        ]
        City.objects.using(db_alias).bulk_create(cities, ignore_conflicts=True)

    for city in City.objects.using(db_alias).select_related("state").all():
        zip_codes = [
            ZipCode(city=city, name=zip_code_name, slug=slugify(zip_code_name))
            for zip_code_name in us_geo_data[
                (us_geo_data[CITY_COLUMN] == city.name)
                & (us_geo_data[STATE_COLUMN] == city.state.name)
            ][ZIP_COLUMN].unique()
        ]
        ZipCode.objects.using(db_alias).bulk_create(zip_codes, ignore_conflicts=True)


class Migration(migrations.Migration):
    dependencies = [("site_configuration", "0001_initial")]
    operations = [migrations.RunPython(create_locations, migrations.RunPython.noop)]
