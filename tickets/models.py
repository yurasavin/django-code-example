from django.db import models
from django.urls import reverse

from contracts.models import ContractNum
from core.cache import delete_reestr_cache


class Ticket(models.Model):
    """
    Модель заявки на закупку. Содержит в себе основные особенности будующей
    закупки/контракта и информацию о лицах относящихся к заявке
    """

    class Meta:
        verbose_name = 'заявка'
        verbose_name_plural = 'заявки'
        ordering = ['-date', '-pk']

    name = models.CharField('Предмет закупки', max_length=100)
    date = models.DateField('Дата получения', auto_now_add=True, db_index=True)
    worker = models.ForeignKey(
        'worker.Worker',
        verbose_name='Ответственный',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={
            'username__in': ['Васильев', 'Луговская', 'Терехова', 'Чернышенко']
        }
    )

    initiators = (
        (1, "Жукова О.С."),
        (2, "Не определен"),
        (3, "Голицын А.В."),
        (4, "Кольба С.В."),
        (5, "Бабаева Ю.С."),
        (6, "Лобанова И.В."),
        (7, "Петрикеева О.А."),
        (8, "Пучкова О.Е."),
        (9, "Михайлова Е.А."),
        (10, "Резникова О.Ю."),
        (11, "Гончаренко И.В.")
    )

    initiator = models.PositiveSmallIntegerField(
        'Инициатор закупки',
        choices=initiators
    )
    filial = models.ForeignKey(
        'Filial',
        verbose_name='Филиал',
        on_delete=models.SET_NULL,
        null=True,
    )
    tender_type = models.ForeignKey(
        'tenders.TenderType',
        verbose_name='Способ закупки',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    under_types = (
        ('drugs', 'лекарства'),
        ('med_izd', 'мед. изделия'),
        ('laboratory', 'лаборатория'),
        ('anti_terror', 'антитерор'),
        ('anti_fire', 'противопожарка'),
        ('remont', 'ремонт'),
    )
    under_type = models.CharField(
        verbose_name='Подтип закупки',
        max_length=11,
        choices=under_types,
        default='',
        blank=True
    )
    statuses = (
        (True, 'В работе'),
        (False, 'Завершена'),
    )
    status = models.BooleanField(
        "Статус",
        max_length=10,
        choices=statuses,
        default=True
    )
    year = models.ManyToManyField(
        'limits.Limit',
        verbose_name='Годы лимитов',
        db_index=True,
    )

    def __str__(self):
        return f'{self.name} - {self.tender_type}'

    def get_absolute_url(self):
        return reverse('tickets:reestr_by_year', args=[self.year.first().year])

    def get_num(self):
        """Возвращает номер контракта для формы"""
        num = ContractNum.objects.get(pk=1)
        return f'{num.num}{self.filial.postfix}'

    def save(self, *args, **kwargs):
        """
        Extend родительский метод
        Удаляет кеш реестра
        """
        super().save(*args, **kwargs)
        for limit in self.year.all():
            year = limit.year
            delete_reestr_cache(year)

    def delete(self, *args, **kwargs):
        """
        Extend родительский метод
        Удаляет кеш реестра
        """
        for limit in self.year.all():
            year = limit.year
            delete_reestr_cache(year)
        super().delete(*args, **kwargs)


class Filial(models.Model):
    """Модель филиала"""
    name = models.CharField(max_length=30)
    postfix = models.CharField(max_length=2, blank=True)

    def __str__(self):
        return self.name
