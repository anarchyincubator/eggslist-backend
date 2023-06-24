import pandas as pd
from django.conf import settings
from django.contrib.gis.geos.point import Point
from django.db import migrations
from django.utils.text import slugify


def remove_current_locations(apps, schema_editor):
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

    db_alias = schema_editor.connection.alias
    ZipCode.objects.using(db_alias).all().delete()
    City.objects.using(db_alias).all().delete()
    State.objects.using(db_alias).all().delete()

    print("Removed current locations")


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
    STATE_ID_COLUMN = "state_id"
    STATE_NAME_COLUMN = "state_name"
    ZIP_COLUMN = "zip"
    db_alias = schema_editor.connection.alias

    us_country = Country.objects.using(db_alias).get(name="United States")
    us_geo_data = pd.read_csv(settings.GEO_ZIP_PATH)

    states = []
    state_ids = us_geo_data[STATE_ID_COLUMN].unique()
    state_names = us_geo_data[STATE_NAME_COLUMN].unique()

    for state_id, state_name in zip(state_ids, state_names):
        states.append(
            State(name=state_id, full_name=state_name, country=us_country, slug=slugify(state_id))
        )

    State.objects.using(db_alias).bulk_create(states)
    print("Created states")
    for state in State.objects.using(db_alias).all():
        cities = []
        city_names = us_geo_data[us_geo_data[STATE_ID_COLUMN] == state.name][CITY_COLUMN].unique()
        for city_name in city_names:
            city_from_df = us_geo_data[
                (us_geo_data[CITY_COLUMN] == city_name)
                & (us_geo_data[STATE_ID_COLUMN] == state.name)
            ].iloc[0, :]
            city_location = Point(x=city_from_df.city_lng, y=city_from_df.city_lat)
            cities.append(
                City(
                    name=city_name,
                    state=state,
                    location=city_location,
                    slug=slugify(city_from_df.city_state),
                )
            )

        City.objects.using(db_alias).bulk_create(cities)

    print("Created cities")

    for city in City.objects.using(db_alias).select_related("state").all():
        zip_codes = []

        df_filter_by_city = us_geo_data[
            (us_geo_data[CITY_COLUMN] == city.name)
            & (us_geo_data[STATE_ID_COLUMN] == city.state.name)
        ]

        for i, zip_code_row in df_filter_by_city.iterrows():
            zip_code_name = str(zip_code_row.zip)
            zip_code_name_adj = (
                "0" + zip_code_name if len(zip_code_name) < 5 else zip_code_name
            )

            zip_code_location = Point(x=zip_code_row.lng, y=zip_code_row.lat)
            zip_codes.append(
                ZipCode(
                    name=zip_code_name_adj,
                    slug=slugify(zip_code_name_adj),
                    city=city,
                    location=zip_code_location,
                )
            )

        ZipCode.objects.using(db_alias).bulk_create(zip_codes)
        print("Creatted Zip Codes")


class Migration(migrations.Migration):
    dependencies = [("site_configuration", "0008_alter_faq_options_alter_teammember_options_and_more")]
    operations = [
        migrations.RunPython(remove_current_locations, migrations.RunPython.noop),
        migrations.RunPython(create_locations, migrations.RunPython.noop),
    ]
