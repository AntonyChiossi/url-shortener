"""
@file serializers.py
@author Antony Chiossi
"""
from datetime import datetime
from django.utils import timezone
import pytz
from rest_framework import serializers

from urls.models import URL
import urllib


class URLSerializer(serializers.Serializer):
    short_id = serializers.CharField(max_length=12)
    long_url = serializers.CharField(max_length=2048)
    expires_at = serializers.DateTimeField(
        required=False, default_timezone=pytz.timezone("UTC")
    )

    def create(self, validated_data):
        expires_at: datetime = validated_data.get("expires_at", None)
        if expires_at:
            expires_at = expires_at.astimezone(timezone.utc)
        url = URL.objects.create(
            short_id=validated_data["short_id"],
            long_url=validated_data["long_url"],
            expires_at=expires_at,
        )
        return url

    def validate_expires_at(self, value):
        """
        Check that expires_at is greater than the current time.
        """
        if value and value < timezone.now():
            raise serializers.ValidationError("expires_at must be in the future.")
        return value

    def validate_long_url(self, value):
        """
        Check that long_url is a valid web URI.
        """
        try:
            parsed_url = urllib.parse.urlparse(value)
        except ValueError:
            raise serializers.ValidationError("Invalid URL format.")
        if parsed_url.scheme not in ["http", "https", "ftp", "ftps"]:
            raise serializers.ValidationError("Invalid URL scheme.")
        if not parsed_url.netloc:
            raise serializers.ValidationError("Invalid URL format.")
        return value
