# Generated by Django 2.2.1 on 2020-02-01 17:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webshopApp', '0002_purchase_cart'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchase',
            name='cart',
        ),
    ]
