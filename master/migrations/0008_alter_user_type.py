# Generated by Django 3.2.4 on 2021-07-10 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0007_alter_user_managers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='type',
            field=models.CharField(choices=[('t', 'استاد'), ('s', 'دانشجو')], max_length=1, verbose_name='نقش'),
        ),
    ]