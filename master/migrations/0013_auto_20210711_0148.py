# Generated by Django 3.2.4 on 2021-07-10 22:18

import django.core.validators
from django.db import migrations, models
import master.models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0012_auto_20210710_1658'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={},
        ),
        migrations.AlterField(
            model_name='user',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to=master.models.user_photo_directory_path, validators=[django.core.validators.FileExtensionValidator(['jpg', 'png', 'jpeg']), master.models.validate_image_size], verbose_name='تصویر پروفایل'),
        ),
        migrations.DeleteModel(
            name='Identity',
        ),
    ]