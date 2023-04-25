"""
@file models.py
@author Antony Chiossi
"""

from django.db import models


class URL(models.Model):
    short_id = models.CharField(max_length=12, unique=True)
    long_url = models.CharField(max_length=2048)
    expires_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class Click(models.Model):
    url = models.URLField()
    user_agent = models.CharField(max_length=255, null=True)
    ip_address = models.GenericIPAddressField(null=True)
    referrer = models.URLField(null=True)
    date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]
