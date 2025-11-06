from django import template
from datetime import timedelta, date

register = template.Library()

def add_months(orig_date, months):
    y = orig_date.year + (orig_date.month - 1 + months) // 12
    m = (orig_date.month - 1 + months) % 12 + 1
    d = min(orig_date.day, [31,
        29 if y % 4 == 0 and not y % 100 == 0 or y % 400 == 0 else 28,
        31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m-1])
    return date(y, m, d)

@register.filter
def prox_mes(orig_date, qtde):
    try:
        qtde = int(qtde)
        return add_months(orig_date, qtde)
    except Exception:
        return orig_date

@register.filter
def times(value, arg):
    try:
        return int(value) * int(arg)
    except Exception:
        return 0
