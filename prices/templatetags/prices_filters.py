from django import template


register = template.Library()


def print_money(money):
    """
    Принимает число в формате Decimal,
    возвращает строку формата "1 123 456.78"
    """
    if not money:
        return '-'
    str_money = str(money)
    if '.' in str_money:
        rub, cop = str_money.split('.')
        cop = cop[:2]
    else:
        rub, cop = str_money, '00'
    out = rub[-3:]
    rub = rub[:-3]
    while rub:
        out = f'{rub[-3:]} {out}'
        rub = rub[:-3]
    return out + ',' + cop


def difference(money1, money2):
    """Возвращает разность двух сумм в читаемом виде"""
    money2 = money2 if money2 else 0
    return money1 - money2

def my_sum(money1, money2):
    """Возвращает сумму двух сумм в читаемом виде"""
    money2 = money2 if money2 else 0
    return money1 + money2


def percent(total, balance):
    """Возвращает значение второго числа в процентах от первого"""
    value = (total - balance) / total * 100
    return f'{value:.2f}'


register.filter('print_money', print_money)
register.filter('difference', difference)
register.filter('percent', percent)
register.filter('my_sum', my_sum)
