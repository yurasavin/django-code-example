# Generated by Django 2.1.7 on 2019-05-25 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenders', '0002_tender_ticket'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tendertype',
            name='sp_equal_cp',
        ),
        migrations.AddField(
            model_name='tendertype',
            name='buy_from_singe_supplier',
            field=models.BooleanField(default=False, verbose_name='Закупка у единственного поставщика'),
            preserve_default=False,
        ),
    ]
