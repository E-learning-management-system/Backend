# Generated by Django 3.2.4 on 2021-10-10 13:00

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import master.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('name', models.CharField(blank=True, max_length=20, null=True, verbose_name='نام')),
                ('university', models.CharField(blank=True, max_length=50, null=True, verbose_name='دانشگاه')),
                ('email', models.EmailField(blank=True, max_length=100, null=True, unique=True, verbose_name='ایمیل')),
                ('password', models.TextField(max_length=2000, verbose_name='رمز عبور')),
                ('password_confirmation', models.TextField(blank=True, max_length=2000, null=True, verbose_name='تکرار رمز عبور')),
                ('type', models.CharField(blank=True, choices=[('a', 'ادمین'), ('t', 'استاد'), ('s', 'دانشجو')], max_length=1, null=True, verbose_name='نقش')),
                ('is_staff', models.BooleanField(default=False, verbose_name='کارمند')),
                ('is_superuser', models.BooleanField(default=False, verbose_name='ابرکاربر')),
                ('code', models.IntegerField(blank=True, null=True, verbose_name='کد یکبار مصرف')),
                ('bio', models.CharField(blank=True, max_length=30, null=True, verbose_name='بیو')),
                ('photo', models.ImageField(blank=True, null=True, upload_to=master.models.user_photo_directory_path, validators=[django.core.validators.FileExtensionValidator(['jpg', 'png', 'jpeg']), master.models.validate_image_size], verbose_name='تصویر پروفایل')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ عضویت')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'کاربر',
                'verbose_name_plural': 'کاربران',
                'ordering': ['date_joined'],
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='عنوان')),
                ('description', models.TextField(blank=True, max_length=1000, null=True, verbose_name='توضیحات')),
                ('start_date', models.DateTimeField(default=None, verbose_name='تاریخ آغاز')),
                ('end_date', models.DateTimeField(verbose_name='تاریخ پایان')),
                ('exam_date', models.DateTimeField(verbose_name='تاریخ امتحان')),
            ],
            options={
                'verbose_name': 'درس',
                'verbose_name_plural': 'درس ها',
                'ordering': ['-title'],
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(blank=True, default=None, max_length=50, null=True, verbose_name='موضوع')),
                ('text', models.TextField(verbose_name='متن')),
                ('date', models.DateTimeField(auto_now_add=True, null=True, verbose_name='تاریخ')),
                ('file', models.FileField(blank=True, help_text='Image size should be less than 1.0\xa0MB', null=True, upload_to=master.models.post_image_directory_path, validators=[django.core.validators.FileExtensionValidator(['png', 'jpg', 'jpeg']), master.models.validate_image_size], verbose_name='فایل')),
                ('course', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='master.course', verbose_name='درس')),
                ('poster', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='post_user', to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={
                'verbose_name': 'پست',
                'verbose_name_plural': 'پست ها',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Support',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='نام و نام خانوادگی')),
                ('email', models.EmailField(max_length=254, verbose_name='ایمیل')),
                ('phone', models.CharField(max_length=15, verbose_name='شماره همراه')),
                ('subject', models.CharField(max_length=50, verbose_name='موضوع')),
                ('description', models.CharField(max_length=2000, verbose_name='متن پیام')),
                ('date', models.DateTimeField(auto_now_add=True, null=True, verbose_name='تاریخ')),
            ],
            options={
                'verbose_name': 'پشتیبانی',
                'verbose_name_plural': 'پشتیبانی ها',
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='عنوان')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master.course', verbose_name='درس')),
            ],
            options={
                'verbose_name': 'مبحث',
                'verbose_name_plural': 'مباحث',
            },
        ),
        migrations.CreateModel(
            name='PostLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True, null=True, verbose_name='ایجاد شده در: ')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_like', to='master.post', verbose_name='پست')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={
                'verbose_name': 'لایک',
                'verbose_name_plural': 'لایک ها',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='PostComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='متن')),
                ('date', models.DateTimeField(auto_now_add=True, null=True, verbose_name='ایجاد شده در: ')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_post', to='master.post', verbose_name='پست')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={
                'verbose_name': 'کامنت',
                'verbose_name_plural': 'کامنت ها',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True, verbose_name='عنوان')),
                ('description', models.TextField(max_length=1000)),
                ('date', models.DateTimeField(auto_now_add=True, null=True, verbose_name='تاریخ ایجاد')),
                ('deadline', models.DateTimeField(null=True, verbose_name='مهلت تحویل')),
                ('file', models.FileField(blank=True, help_text='Image size should be less than 1.0\xa0MB', null=True, upload_to=master.models.exercise_image_directory_path, validators=[django.core.validators.FileExtensionValidator(['png', 'jpg', 'jpeg']), master.models.validate_image_size], verbose_name='فایل')),
                ('author', models.ForeignKey(limit_choices_to={'type': 't'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='استاد')),
                ('course', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='master.course', verbose_name='درس')),
                ('subject', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='master.subject', verbose_name='مبحث')),
            ],
            options={
                'verbose_name': 'تمرین',
                'verbose_name_plural': 'تمرین ها',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='CourseStudent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master.course', verbose_name='درس')),
                ('user', models.ForeignKey(limit_choices_to={'type': 's'}, on_delete=django.db.models.deletion.CASCADE, related_name='student_course', to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={
                'verbose_name': 'دانشجو',
                'verbose_name_plural': 'دانشجویان',
            },
        ),
        migrations.AddField(
            model_name='course',
            name='student',
            field=models.ManyToManyField(blank=True, through='master.CourseStudent', to=settings.AUTH_USER_MODEL, verbose_name='دانشجویان'),
        ),
        migrations.AddField(
            model_name='course',
            name='teacher',
            field=models.ForeignKey(limit_choices_to={'type': 't'}, on_delete=django.db.models.deletion.CASCADE, related_name='teacher_course', to=settings.AUTH_USER_MODEL, verbose_name='استاد'),
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(max_length=1000)),
                ('date', models.DateTimeField(auto_now_add=True, null=True, verbose_name='تاریخ بارگزاری')),
                ('file', models.FileField(blank=True, help_text='Image size should be less than 1.0\xa0MB', null=True, upload_to=master.models.exercise_ans_image_directory_path, validators=[django.core.validators.FileExtensionValidator(['png', 'jpg', 'jpeg']), master.models.validate_image_size], verbose_name='فایل')),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master.exercise', verbose_name='تمرین')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='دانشجو')),
            ],
            options={
                'verbose_name': 'پاسخ',
                'verbose_name_plural': 'پاسخ ها',
                'ordering': ['-date'],
            },
        ),
    ]
