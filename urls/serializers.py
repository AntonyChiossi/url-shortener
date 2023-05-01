"""
@file serializers.py
@author Antony Chiossi
"""

import re
import pytz
import urllib
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from urls.models import URL
from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = get_user_model()
        fields = ["id", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def validate_password(self, password: str):
        """
        Validate password to meet NIST guidelines
        """
        min_length = 12
        max_length = 128
        if len(password) < min_length:
            raise serializers.ValidationError(
                "Password must be at least {} characters.".format(min_length)
            )
        if len(password) > max_length:
            raise serializers.ValidationError(
                "Password must be at most {} characters.".format(max_length)
            )
        if password.isnumeric() or password.isalpha():
            raise serializers.ValidationError(
                "Password must contain at least one number and one letter."
            )
        if password.islower() or password.isupper() or password.isnumeric():
            raise serializers.ValidationError(
                "Password must contain at least one lowercase letter, one uppercase letter, and one symbol."
            )
        return password


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data) -> User:
        email = data.get("email", None)
        password = data.get("password", None)

        if not email or not password:
            raise serializers.ValidationError("Both email and password are required.")

        print("Authenticating with {}:{}".format(email, password))
        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid login credentials.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        return user


class URLSerializer(serializers.Serializer):
    short_id = serializers.CharField(max_length=12)
    long_url = serializers.CharField(min_length=3, max_length=2048)
    expires_at = serializers.DateTimeField(
        required=False, default_timezone=pytz.timezone("UTC")
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False
    )

    def create(self, validated_data):
        expires_at: datetime = validated_data.get("expires_at", None)
        if expires_at:
            expires_at = expires_at.astimezone(timezone.utc)
        url = URL.objects.create(
            short_id=validated_data["short_id"],
            long_url=validated_data["long_url"],
            expires_at=expires_at,
            user=validated_data.get("user", None),
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
