from django.db.models import Model, TextChoices, CharField, ForeignKey, CASCADE, PositiveIntegerField, \
    FileField, F, Sum

from apps.models.base import CreatedBaseModel


class Order(CreatedBaseModel):
    class Status(TextChoices):
        PROCESSING = 'processing', 'Processing'
        ON_HOLD = 'on_hold', 'On Hold'
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'

    class PaymentMethod(TextChoices):
        PAYPAL = 'paypal', 'Paypal'
        CREDIT_CARD = 'credit_card', 'Credit_card'

    status = CharField(max_length=25, choices=Status.choices, default=Status.PROCESSING)

    payment_method = CharField(max_length=255, choices=PaymentMethod.choices)
    address = ForeignKey('apps.Address', CASCADE)
    owner = ForeignKey('apps.User', CASCADE, related_name='orders')
    pdf_file = FileField()

    def __str__(self):
        return f'Order {self.id} - {self.status}'

    @property
    def total(self):
        return self.orderitem_set.aggregate(
            total=Sum(F('quantity') * (F('product__price') * (
                    100 - F('product__discount_percent')) / 100)) + Sum(F('product__shipping_cost'))
        )


class OrderItem(Model):
    product = ForeignKey('Product', CASCADE)
    order = ForeignKey('Order', CASCADE)
    quantity = PositiveIntegerField(default=1)

    @property
    def amount(self):
        return self.quantity * self.product.current_price
