"""
@file tasks.py
@author Antony Chiossi
"""


from celery import shared_task
from urls.models import Click
from urls.models import URL
from django.utils import timezone
from django.contrib.auth.models import User

from utils.commons import deliver_email

now = timezone.now()


@shared_task
def track_click(url_pk, user_agent, ip_address, referrer, date):
    url = URL.objects.get(pk=url_pk)
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
        if url_chunk.user:
            # TODO for better performance aggregate by user an send 1 mail with all clicks stats
            user = User.objects.get(pk=url_chunk.user)
            stats = url_chunk.clicks.all()
            send_email.delay(user.email, stats)
        click_ids = Click.objects.filter(url=url_chunk).values_list("id", flat=True)[
            :chunk_size
        ]
        Click.objects.filter(id__in=click_ids).delete()

    expired_urls.delete()


@shared_task
def send_email(email, stats):
    deliver_email(email=email, stats=stats)
