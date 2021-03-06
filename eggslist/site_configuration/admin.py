from django.contrib import admin

from eggslist.site_configuration import models


@admin.register(models.LocationCountry)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    readonly_fields = ("slug",)


@admin.register(models.LocationState)
class StateAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    list_select_related = ("country",)
    readonly_fields = ("slug",)


@admin.register(models.LocationCity)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "state")
    list_select_related = ("state",)
    readonly_fields = ("slug",)


@admin.register(models.LocationZipCode)
class ZipCodeAdmin(admin.ModelAdmin):
    list_display = ("name", "city")
    list_select_related = ("city",)
    readonly_fields = ("slug",)


@admin.register(models.Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("author_name", "body")


@admin.register(models.FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "answer")
