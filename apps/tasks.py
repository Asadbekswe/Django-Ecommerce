from celery import shared_task
from django.core.mail import send_mail

from apps.models import User
from core import settings


@shared_task
def send_to_email(subject, email):
    users = User.objects.all()
    for user in users:
        send_mail(
            subject,
            'Your account has been created successfully.',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
            # from_email=email,
            # send_to_email=user.email,
        )



                