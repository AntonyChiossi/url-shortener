"""
@file tasks.py
@author Antony Chiossi
"""


from celery import shared_task

from urls.models import Click
from urls.models import URL
from django.utils import timezone


now = timezone.now()
expired_urls = URL.objects.filter(expires_at__lte=now)
print("now: ", now)
print("expired_urls:")
print(expired_urls)
# click = Click(
#     url="aaaaaa",
#     user_agent=None,
#     ip_address=None,
#     referrer=None,
#     date=None,
# )
# click.save()
# print(click)


@shared_task
def track_click(url, user_agent, ip_address, referrer, date):
    click = Click(
        url=url,
        user_agent=user_agent,
        ip_address=ip_address,
        referrer=referrer,
        date=date,
    )
    click.save()


@shared_task
def delete_expired_urls():
    now = timezone.now()
    expired_urls = URL.objects.filter(expires_at__lte=now)

    chunk_size = 10000
    for url_chunk in expired_urls.iterator(chunk_size=chunk_size):
        click_ids = Click.objects.filter(url=url_chunk).values_list("id", flat=True)[
            :chunk_size
        ]
        Click.objects.filter(id__in=click_ids).delete()

    expired_urls.delete()
