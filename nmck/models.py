# from django.db import models


# class Nmck(models.Model):
#     """
#     Модель начальной максимальной цены контракта
#     """
#     worker = models.ForeignKey('worker.Worker', verbose_name='Исполнитель')


# class Position(models.Model):
#     """
#     Модель позиции НМЦК
#     """
#     name = models.TextField('Наименование')
#     price1 = models.DecimalField('Цена №1', max_digits=7, decimal_places=2)
#     price2 = models.DecimalField('Цена №2', max_digits=7, decimal_places=2)
#     price3 = models.DecimalField('Цена №3', max_digits=7, decimal_places=2)
#     nmck = models.ForeignKey(Nmck, verbose_name='НМЦК')
