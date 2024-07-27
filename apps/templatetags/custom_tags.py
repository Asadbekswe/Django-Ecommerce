import re
from datetime import datetime
from decimal import Decimal

from django.template import Library
from django.utils.formats import number_format

register = Library()


@register.filter()
def editor_phone_number(value, arg=None) -> str:
    if value.startswith('+998'):
        return value
    return f"+998{value}"


@register.filter()
def is_liked(user, product) -> bool:
    if user.is_anonymous:
        return False
    return user.favorite_set.filter(product=product).exists()


@register.filter(is_safe=True)
def cart_intcomma(value, use_l10n=True):
    if use_l10n:
        try:
            if not isinstance(value, (float, Decimal)):
                value = int(value)
        except (TypeError, ValueError):
            return cart_intcomma(value, False)
        else:
            return number_format(value, use_l10n=True, force_grouping=True)
    result = str(value)
    match = re.match(r"-?\d+", result)
    if match:
        prefix = match[0]
        prefix_with_commas = re.sub(r"\d{4}", r"\g<0>,", prefix[::-1])[::-1]
        prefix_with_commas = re.sub(r"^(-?) ", r"\1", prefix_with_commas)
        result = prefix_with_commas + result[len(prefix):]
    return result


@register.filter(name='is_expired')
def is_expired(exp_date):
    try:
        exp_month, exp_year = exp_date.split('/')
        exp_year = int(exp_year) + 2000
        exp_month = int(exp_month)

        current_date = datetime.now()
        if current_date.year > exp_year:
            return True
        elif current_date.year == exp_year and current_date.month > exp_month:
            return True
        else:
            return False
    except ValueError:
        return True


@register.filter(name='format_exp_date')
def format_exp_date(exp_date):
    try:
        exp_month, exp_year = exp_date.split('/')
        exp_year = int(exp_year) + 2000
        return f"{exp_month}/{exp_year}"
    except ValueError:
        return exp_date


@register.filter()
def multiplication(a, b):
    return a * b


@register.filter()
def tax_sum(a, b):
    return a * b // 100


@register.filter()
def total_sum(a, b):
    return a + b
