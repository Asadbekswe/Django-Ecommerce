from django.contrib.admin import register, action, StackedInline, ModelAdmin
from django.db.models import F
from import_export.admin import ImportExportModelAdmin
from mptt.admin import DraggableMPTTAdmin

from apps.models import Product, ProductImage, Category, Tag, SiteSettings
from apps.models.products import Review


class ProductImageStackedInline(StackedInline):
    model = ProductImage
    extra = 2
    min_num = 0


@register(Product)
class Product(ModelAdmin):
    list_display = 'title', 'in_stock', 'price'
    inlines = [ProductImageStackedInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            # kwargs["queryset"] = Category.objects.filter(children__isnull=True)
            # kwargs["queryset"] = Category.objects.filter(lft=F('rght') - 1)
            kwargs["queryset"] = Category.objects.filter(rght=F('lft') + 1)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @action(description='Sotuvda bormi?')
    def get_in_stock(self, obj: Product):
        return obj.in_stock

    get_in_stock.boolean = True


@register(Category)
class CategoryModelAdmin(DraggableMPTTAdmin, ImportExportModelAdmin):
    pass


@register(Review)
class ReviewModelAdmin(ModelAdmin):
    list_display = 'id', 'date_posted', 'rating', 'product'
    readonly_fields = ['date_posted']


@register(Tag)
class TagModelAdmin(ModelAdmin):
    pass


@register(SiteSettings)
class Tax(ModelAdmin):
    pass
