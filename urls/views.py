"""
@file view.py
@author Antony Chiossi
"""


# urls/views.py

from django.http import (
    Http404,
    HttpResponseNotFound,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from shortener.tasks import track_click
from utils.commons import snowflake_to_base62
from utils.snowflake import Snowflake
from urls.models import URL
from urls.serializers import URLSerializer
from django.shortcuts import render
from django.utils import timezone

# can handle 4096 IDs per node per millisecond
snowflake = Snowflake(1, 1)


def custom_404_view(request, exception):
    return render(request, "404.html", status=404)


@api_view(["POST"])
def create_url(request):
    data = {
        "short_id": snowflake_to_base62(snowflake.generate_snowflake_id()),
        "long_url": request.data.get("long_url", ""),
        "expires_at": request.data.get("expires_at", None),
    }
    serializer = URLSerializer(data=data)
    if serializer.is_valid():
        url = serializer.save()
        return Response({"short_id": url.short_id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_url(request, short_id):
    print("short_id: ", short_id)

    try:
        url = get_object_or_404(URL, short_id=short_id)
        print("url: ", url)
        print("expire: ", url.expires_at, timezone.now())
        if url.expires_at and url.expires_at < timezone.now():
            return HttpResponseNotFound("The URL has expired.")

        track_click.delay(
            url=short_id,
            user_agent=request.META.get("HTTP_USER_AGENT"),
            ip_address=request.META.get("REMOTE_ADDR"),
            referrer=request.META.get("HTTP_REFERER"),
            date=timezone.now(),
        )
        response = HttpResponseRedirect(url.long_url)
        response["cache-control"] = "no-cache, no-store, max-age=0, must-revalidate"
        response["Pragma"] = "no-cache"
        response["Expires"] = "Mon, 01 Jan 1990 00:00:00 GMT"
        return response
    except Http404:
        return render(request, "404.html", status=404)


@api_view(["GET"])
def get_url_stats(request, short_id):
    url = get_object_or_404(URL, short_id=short_id)
    stats = {
        "short_id": url.short_id,
        "long_url": url.long_url,
        "expires_at": url.expires_at,
        "created_at": url.created_at,
        "updated_at": url.updated_at,
    }
    return Response(stats)
