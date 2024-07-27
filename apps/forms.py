from datetime import datetime

from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.forms import ModelForm, CharField, ModelChoiceField
from django_recaptcha.fields import ReCaptchaField

from apps.models import Address, Order, CreditCard, OrderItem, User
from apps.models.products import Review, CartItem


class RecaptchaForm(AuthenticationForm):
    captcha = ReCaptchaField()


class UserRegisterModelForm(ModelForm):
    password2 = CharField(max_length=128)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password and password2 and password != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)


class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'name', 'email', 'review_text']


class AddressForm(ModelForm):
    class Meta:
        model = Address
        fields = ('full_name', 'street', 'phone', 'zip_code', 'city')


class OrderCreateModelForm(ModelForm):
    address = ModelChoiceField(queryset=Address.objects.all())
    owner = ModelChoiceField(queryset=User.objects.all(), required=False)

    class Meta:
        model = Order
        fields = 'payment_method', 'address', 'owner'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        obj: Order = super().save(commit=False)

        if not obj.owner:
            obj.owner = self.request.user

        if commit:
            obj.save()

            if obj.payment_method == 'credit_card':
                cvv = self.data.get('cvv')
                month, year = map(int, self.data.get('expire_date').split('/'))
                expire_date = datetime(year + 2000, month, 1).date()
                number = self.data.get('number')
                CreditCard.objects.create(
                    owner=obj.owner,
                    order=obj,
                    cvv=cvv,
                    expire_date=expire_date,
                    number=number
                )

            for cart_item in obj.owner.cart_items.all():
                OrderItem.objects.create(
                    order=obj,
                    quantity=cart_item.quantity,
                    product=cart_item.product
                )

            CartItem.objects.filter(user=obj.owner).delete()

        return obj
