# Generated by Django 2.1.7 on 2019-03-30 09:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tenders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Filial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('postfix', models.CharField(blank=True, max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Предмет закупки')),
                ('date', models.DateField(auto_now_add=True, db_index=True, verbose_name='Дата получения')),
                ('initiator', models.PositiveSmallIntegerField(choices=[(1, 'Жукова О.С.'), (2, 'Не определен'), (3, 'Голицын А.В.'), (4, 'Кольба С.В.'), (5, 'Бабаева Ю.С.'), (6, 'Лобанова И.В.'), (7, 'Петрикеева О.А.'), (8, 'Пучкова О.Е.'), (9, 'Михайлова Е.А.'), (10, 'Резникова О.Ю.'), (11, 'Гончаренко И.В.')], verbose_name='Инициатор закупки')),
                ('rating', models.PositiveSmallIntegerField(blank=True, choices=[(0, 'Очень легко'), (1, 'Легко'), (2, 'Нормально'), (3, 'Сложно'), (4, 'Очень сложно')], null=True, verbose_name='Сложность')),
                ('under_type', models.CharField(blank=True, choices=[('drugs', 'лекарства'), ('med_izd', 'мед. изделия'), ('laboratory', 'лаборатория'), ('anti_terror', 'антитерор'), ('anti_fire', 'противопожарка'), ('remont', 'ремонт')], default='', max_length=11, verbose_name='Подтип закупки')),
                ('status', models.BooleanField(choices=[(True, 'В работе'), (False, 'Завершена')], default=True, max_length=10, verbose_name='Статус')),
                ('filial', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tickets.Filial', verbose_name='Филиал')),
                ('tender_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tenders.TenderType', verbose_name='Способ закупки')),
            ],
            options={
                'verbose_name': 'заявка',
                'verbose_name_plural': 'заявки',
                'ordering': ['-date', '-pk'],
            },
        ),
    ]
