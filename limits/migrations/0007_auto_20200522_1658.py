# Generated by Django 3.0.6 on 2020-05-22 13:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('limits', '0006_auto_20200514_1235'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='debt',
            options={'verbose_name': 'Кредиторская задолженность', 'verbose_name_plural': 'Кредиторские задолженности'},
        ),
    ]
