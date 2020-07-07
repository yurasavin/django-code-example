"""Модуль для работы с кешем"""
import hashlib
from django.core.cache import cache
# Чтобы посмотреть ключи в кеше:
# from memcached_stats import MemcachedStats
# mem = MemcachedStats()
# mem.keys()


def get_md5_int_hash(num):
    """
    Возвращает ключ для кеша в шаблоне,
    преобразует число в хеш md5 если передано
    """
    return hashlib.md5(f"{num}".encode('utf-8')).hexdigest()


def delete_reestr_cache(year):
    """Удаляет кеш реестра"""
    key = f'template.cache.reestr.{get_md5_int_hash(year)}'
    cache.delete(key)
