from rest_framework import serializers

from eggslist.site_configuration import models


class StateLocationSerializer(serializers.ModelSerializer):
    country = serializers.CharField(source="country.name")

    class Meta:
        model = models.LocationState
        fields = ("slug", "name", "country")


class CityLocationSerializer(serializers.ModelSerializer):
    state = serializers.CharField(source="state.name")
    state_full_name = serializers.CharField(source="state.full_name")
    country = serializers.CharField(source="state.country.name")

    class Meta:
        model = models.LocationCity
        fields = ("slug", "name", "state_full_name", "state", "country")


class ZipCodeLocationSerializer(serializers.ModelSerializer):
    city = serializers.CharField(source="city.name")
    state = serializers.CharField(source="city.state.name")
    state_full_name = serializers.CharField(source="city.state.full_name")

    class Meta:
        model = models.LocationZipCode
        fields = ("slug", "name", "state", "state_full_name", "city")


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Testimonial
        fields = ("author_name", "body")


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FAQ
        fields = ("question", "answer")


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TeamMember
        fields = ("first_name", "last_name", "image", "job_title")
