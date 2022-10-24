from rest_framework import serializers


class SocialAuthURLSerializer(serializers.Serializer):
    social_url = serializers.URLField()
