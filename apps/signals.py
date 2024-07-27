import os

from allauth.socialaccount.models import SocialAccount
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.models import User


@receiver(post_save, sender=SocialAccount)
def post_save_socialaccount(sender, instance: SocialAccount, **kwargs):
    user: User = instance.user
    photo_url = instance.extra_data.get('photo_url')
    if photo_url:
        import requests
        r = requests.get(photo_url, allow_redirects=True)

        if r.status_code == 200:
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(r.content)
            img_temp.flush()

            try:
                user.image.save(os.path.basename(photo_url), File(img_temp), save=True)
            except:
                pass
