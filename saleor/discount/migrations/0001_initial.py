# Generated by Django 2.0.3 on 2018-07-20 15:03

import datetime
from django.db import migrations, models
import django.db.models.deletion
import django_prices.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('type', models.CharField(choices=[('fixed', 'ARS'), ('percentage', '%')], default='fixed', max_length=10)),
                ('value', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('categories', models.ManyToManyField(blank=True, to='product.Category')),
                ('products', models.ManyToManyField(blank=True, to='product.Product')),
            ],
            options={
                'permissions': (('view_sale', 'Can view sales'), ('edit_sale', 'Can edit sales')),
            },
        ),
        migrations.CreateModel(
            name='Voucher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('value', 'All purchases'), ('product', 'One product'), ('category', 'A category of products'), ('shipping', 'Shipping')], default='value', max_length=20)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('code', models.CharField(db_index=True, max_length=12, unique=True)),
                ('usage_limit', models.PositiveIntegerField(blank=True, null=True)),
                ('used', models.PositiveIntegerField(default=0, editable=False)),
                ('start_date', models.DateField(default=datetime.date.today)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('discount_value_type', models.CharField(choices=[('fixed', 'ARS'), ('percentage', '%')], default='fixed', max_length=10)),
                ('discount_value', models.DecimalField(decimal_places=2, max_digits=12)),
                ('apply_to', models.CharField(blank=True, max_length=20, null=True)),
                ('limit', django_prices.models.MoneyField(blank=True, currency='ARS', decimal_places=2, max_digits=12, null=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='product.Category')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='product.Product')),
            ],
            options={
                'permissions': (('view_voucher', 'Can view vouchers'), ('edit_voucher', 'Can edit vouchers')),
            },
        ),
    ]
