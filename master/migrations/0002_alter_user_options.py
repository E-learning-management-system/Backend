# Generated by Django 3.2.4 on 2021-07-11 19:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['username'], 'verbose_name': 'کاربر', 'verbose_name_plural': 'کاربران'},
        ),
    ]
