# Generated by Django 2.2.1 on 2020-02-01 23:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webshopApp', '0007_auto_20200202_0007'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='user',
        ),
        migrations.AddField(
            model_name='comment',
            name='username',
            field=models.CharField(default='AnonymousUser', max_length=50),
        ),
    ]
