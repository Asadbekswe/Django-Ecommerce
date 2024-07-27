from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db.models import CASCADE, OneToOneField, DateField, Model, \
    ForeignKey, PositiveIntegerField, CharField, FloatField, ImageField, BooleanField

from apps.models.base import CreatedBaseModel


class User(AbstractUser):
    has_pro = BooleanField(default=False)
    image = ImageField(upload_to='users/image/', null=True, blank=True)

    @property
    def cart_count(self):
        return self.cart_items.count()


class CreditCard(CreatedBaseModel):
    owner = ForeignKey('apps.User', CASCADE)
    order = OneToOneField('apps.Order', CASCADE)
    number = CharField(max_length=19, blank=True)
    cvv = CharField(max_length=3)
    expire_date = DateField()


class SiteSettings(Model):
    tax = FloatField(default=0.0)

    def clean(self):
        if self.tax <= 0:
            raise ValidationError({'tax': 'Tax rate must be greater than zero.'})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return F"Tax: {self.tax}%"


class Address(CreatedBaseModel):
    user = ForeignKey('apps.User', CASCADE)
    full_name = CharField(max_length=255)
    street = CharField(max_length=255)
    zip_code = PositiveIntegerField()
    city = CharField(max_length=255)
    phone = CharField(max_length=255)

    def __str__(self):
        return f'{self.full_name} , {self.street}, {self.city}'
