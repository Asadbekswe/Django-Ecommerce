from datetime import timedelta

from django.db.models import CASCADE, Model, CharField, IntegerField, PositiveIntegerField, ManyToManyField, JSONField, \
    ForeignKey, DateTimeField, ImageField, EmailField, TextField, DateField, DecimalField, \
    BooleanField, CheckConstraint, Q
from django.utils.timezone import now
from django_ckeditor_5.fields import CKEditor5Field
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from apps.models.base import SlugBaseModel
from apps.models.user import User


class Category(SlugBaseModel, MPTTModel):
    parent = TreeForeignKey('self', CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']


class Tag(SlugBaseModel):
    pass


class Product(Model):
    title = CharField(max_length=255)
    short_description = CharField(max_length=255)
    price = PositiveIntegerField()
    discount_percent = PositiveIntegerField(default=0, db_default=0)
    shipping_cost = PositiveIntegerField(default=0)
    stock = PositiveIntegerField(default=0)
    long_description = CKEditor5Field()
    tags = ManyToManyField('Tag', blank=True)
    specification = JSONField(default=dict)
    category = ForeignKey('Category', CASCADE, related_name="products")
    is_premium = BooleanField(db_default=False)
    updated_at = DateTimeField(auto_now=True)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            CheckConstraint(
                check=Q(discount_percent__lte=100),
                name="discount_percent__lte__100",
            )
        ]

    @property
    def is_new(self) -> bool:
        return self.created_at >= now() - timedelta(days=7)

    @property
    def current_price(self):
        # return self.price - self.price * self.discount_percent // 100
        return self.price * (100 - self.discount_percent) // 100

    def __str__(self):
        return self.title

    @property
    def in_stock(self) -> bool:
        return self.stock > 0

    # @property
    # def count_review(self):
    #     return self.product_reviews.count()


class ProductImage(Model):
    image = ImageField(upload_to='products/%Y/%m/%d/')
    product = ForeignKey('Product', CASCADE, related_name='images')

    def __str__(self):
        return f"Image for {self.product.title}"


class Review(Model):
    RATINGS = (
        (1, '1 star'),
        (1.5, '1.5 star'),
        (2, '2 stars'),
        (2.5, '2.5 stars'),
        (3, '3 stars'),
        (3.5, ' 3.5 stars'),
        (4, '4 stars'),
        (4.5, '4.5 stars'),
        (5, '5 stars'),
    )
    product = ForeignKey(Product, CASCADE, related_name='reviews')
    rating = IntegerField(choices=RATINGS)
    name = CharField(max_length=255)
    email = EmailField()
    review_text = TextField()
    date_posted = DateField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.name} on {self.date_posted}"


class CartItem(Model):
    product = ForeignKey('apps.Product', CASCADE)
    user = ForeignKey('apps.User', CASCADE, related_name='cart_items')
    quantity = PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product}"

    # @property
    # def amount(self):
        # return self.quantity * self.product


class Favorite(Model):
    user = ForeignKey(User, CASCADE)
    product = ForeignKey('Product', CASCADE)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')


class Coupon(Model):
    code = CharField(max_length=50)
    discount_amount = DecimalField(max_digits=10, decimal_places=2)
    active = BooleanField(default=True)

    def __str__(self):
        return self.code
