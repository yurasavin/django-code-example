# Generated by Django 3.0.6 on 2020-07-08 06:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tenders', '0001_initial'),
        ('tickets', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.CharField(max_length=50)),
                ('date', models.DateField(db_index=True)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=11, null=True)),
                ('specif', models.TextField()),
                ('bank_guar', models.BooleanField()),
                ('pledge', models.DecimalField(decimal_places=2, max_digits=11)),
                ('kontragent', models.CharField(max_length=100)),
                ('tender', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tenders.Tender')),
                ('ticket', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='tickets.Ticket')),
            ],
        ),
        migrations.CreateModel(
            name='ContractChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.CharField(blank=True, max_length=10, verbose_name='Номер')),
                ('date', models.DateField(verbose_name='Дата')),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contracts.Contract')),
            ],
        ),
    ]