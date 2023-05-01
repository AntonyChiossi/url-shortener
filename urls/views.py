"""
@file view.py
@author Antony Chiossi
"""


# urls/views.py

from django.http import (
    Http404,
    HttpResponseNotFound,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
from shortener.tasks import track_click
from utils.commons import is_int, is_str, snowflake_to_base62
from utils.snowflake import Snowflake
from urls.models import URL, Click
from urls.serializers import LoginSerializer, RegistrationSerializer, URLSerializer
from django.shortcuts import render
from django.utils import timezone
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView

# can handle 4096 IDs per node per millisecond
snowflake = Snowflake(1, 1)
MAX_COUNT = 10000


class UrlView(APIView):
    @method_decorator(ratelimit(key="ip", rate="1/s", block=True, method="POST"))
    def post(self, request):
        print("create_url user", request.user)
        print("create_url request.user.is_authenticated", request.user.is_authenticated)

        user = None
        if request.user.is_authenticated:
            user = User.objects.get(**{User.USERNAME_FIELD: request.user})
            data = {
                "short_id": snowflake_to_base62(snowflake.generate_snowflake_id()),
                "long_url": request.data.get("long_url", ""),
                "user": user.pk if request.user.is_authenticated and user else None,
            }
        else:
            data = {
                "short_id": snowflake_to_base62(snowflake.generate_snowflake_id()),
                "long_url": request.data.get("long_url", ""),
            }

        expires_at = request.data.get("expires_at", None)
        if expires_at:
            data["expires_at"] = expires_at

        print("data: ", data)
        serializer = URLSerializer(data=data)
        if serializer.is_valid():
            url = serializer.save()
            return Response({"short_id": url.short_id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        user = None
        if request.user.is_authenticated:
            user = User.objects.get(**{User.USERNAME_FIELD: request.user})
            urls = URL.objects.filter(user=user.pk)

            # Serialize the URLs and return as JSON
            data = URLSerializer(urls, many=True).data
            return JsonResponse(
                {
                    "urls": [
                        {
                            "short_id": x["short_id"],
                            "long_url": x["long_url"],
                            "expires_at": x["expires_at"],
                        }
                        for x in data
                    ]
                }
            )
        return JsonResponse({"details": "You must login"}, status=403)


def custom_404_view(request):
    return render(request, "404.html", status=404)


def angular(request):
    return render(request, "../frontend/index.html", status=200)


@api_view(["POST"])
@csrf_exempt
def register(request):
    try:
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            new_user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
            )
            return Response(
                {"email": new_user.email, "password": password},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except ValidationError as err:
        return JsonResponse(
            {"errors": err.detail},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    except Exception as err:
        print(err)
        return Response(
            {"detail": "Internal Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@ratelimit(key="ip", rate="1/s", block=True, method="POST")
@csrf_exempt
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data
    print("user: {}".format(user))
    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@ratelimit(key="ip", rate="1/s", block=True, method="POST")
def refresh_token(request):
    refresh_token = request.data.get("refresh")
    if refresh_token is None:
        return Response(
            {"detail": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        refresh = RefreshToken(refresh_token)
        access_token = str(refresh.access_token)
        return Response({"access": access_token})
    except Exception:
        return Response(
            {"detail": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["GET"])
def get_url(request, short_id):
    try:
        is_str(short_id)
    except ValidationError as err:
        return Response(
            {"errors": "; ".join(err.messages)},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    try:
        url = get_object_or_404(URL, short_id=short_id)
        if url.expires_at and url.expires_at < timezone.now():
            return HttpResponseNotFound("The URL has expired.")

        track_click.delay(
            url_pk=url.pk,
            user_agent=request.META.get("HTTP_USER_AGENT"),
            ip_address=__get_client_ip(request),
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
def get_url_stats(request, short_id, count=1000):
    try:
        is_int(short_id, default=count)
    except ValidationError as err:
        return Response(
            {"errors": "; ".join(err.messages)},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    try:
        url = get_object_or_404(URL, short_id=short_id)
    except Http404:
        return render(request, "404.html", status=404)
    count = max(count, MAX_COUNT)
    clicks = url.clicks.all()[:count]
    click_data = []
    for click in clicks:
        click_data.append(
            {
                "user_agent": click.user_agent,
                "ip_address": click.ip_address,
                "referrer": click.referrer,
                "date": click.date,
            }
        )
    response_data = {
        "expires_at": url.expires_at,
        "long_url": url.long_url,
        "clicks": click_data,
        "total_clicks": len(click_data),
    }
    return JsonResponse(response_data, status=200)


def __get_client_ip(request):
    ip = None
    try:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
    except Exception as err:
        print(err)
    return ip
