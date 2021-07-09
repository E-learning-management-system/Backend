# Generated by Django 3.2.4 on 2021-07-08 19:22

from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0003_auto_20210615_2015'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExerciseAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(null=True, upload_to='', verbose_name='فایل پاسخ')),
                ('date', models.DateTimeField(auto_now_add=True, null=True, verbose_name='تاریخ بارگزاری')),
            ],
            options={
                'verbose_name': 'پاسخ',
                'verbose_name_plural': 'پاسخ ها',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='عنوان')),
            ],
            options={
                'verbose_name': 'مبحث',
                'verbose_name_plural': 'مباحث',
            },
        ),
        migrations.RemoveField(
            model_name='identity',
            name='user',
        ),
        migrations.AlterModelOptions(
            name='course',
            options={'ordering': ['-title'], 'verbose_name': 'درس', 'verbose_name_plural': 'درس ها'},
        ),
        migrations.AlterModelOptions(
            name='coursestudent',
            options={'verbose_name': 'دانشجو', 'verbose_name_plural': 'دانشجویان'},
        ),
        migrations.AlterModelOptions(
            name='exercise',
            options={'ordering': ['-date'], 'verbose_name': 'تمرین', 'verbose_name_plural': 'تمرین ها'},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-date'], 'verbose_name': 'پست', 'verbose_name_plural': 'پست ها'},
        ),
        migrations.AlterModelOptions(
            name='postcomment',
            options={'ordering': ['-date'], 'verbose_name': 'کامنت', 'verbose_name_plural': 'کامنت ها'},
        ),
        migrations.AlterModelOptions(
            name='postlike',
            options={'ordering': ['-date'], 'verbose_name': 'لایک', 'verbose_name_plural': 'لایک ها'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'verbose_name': 'تگ', 'verbose_name_plural': 'تگ ها'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.RemoveField(
            model_name='exercise',
            name='answer',
        ),
        migrations.RemoveField(
            model_name='post',
            name='codeId',
        ),
        migrations.RemoveField(
            model_name='post',
            name='time',
        ),
        migrations.RemoveField(
            model_name='postcomment',
            name='time',
        ),
        migrations.RemoveField(
            model_name='postlike',
            name='Date',
        ),
        migrations.RemoveField(
            model_name='user',
            name='avatar',
        ),
        migrations.RemoveField(
            model_name='user',
            name='code',
        ),
        migrations.AddField(
            model_name='exercise',
            name='deadline',
            field=models.DateTimeField(null=True, verbose_name='مهلت تحویل'),
        ),
        migrations.AddField(
            model_name='post',
            name='date',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='تاریخ'),
        ),
        migrations.AddField(
            model_name='post',
            name='poster',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='post_user', to=settings.AUTH_USER_MODEL, verbose_name='کاربر'),
        ),
        migrations.AddField(
            model_name='postcomment',
            name='date',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='ایجاد شده در: '),
        ),
        migrations.AddField(
            model_name='postlike',
            name='date',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='ایجاد شده در: '),
        ),
        migrations.AddField(
            model_name='user',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='تصویر پروفایل'),
        ),
        migrations.AlterField(
            model_name='course',
            name='description',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name='توضیحات'),
        ),
        migrations.AlterField(
            model_name='course',
            name='end_date',
            field=models.DateTimeField(verbose_name='تاریخ پایان'),
        ),
        migrations.AlterField(
            model_name='course',
            name='exam_date',
            field=models.DateTimeField(verbose_name='تاریخ امتحان'),
        ),
        migrations.AlterField(
            model_name='course',
            name='start_date',
            field=models.DateTimeField(default=None, verbose_name='تاریخ آغاز'),
        ),
        migrations.AlterField(
            model_name='course',
            name='teacher',
            field=models.ForeignKey(limit_choices_to={'type': 't'}, on_delete=django.db.models.deletion.CASCADE, related_name='teacher_course', to=settings.AUTH_USER_MODEL, verbose_name='استاد'),
        ),
        migrations.AlterField(
            model_name='course',
            name='title',
            field=models.CharField(max_length=255, verbose_name='عنوان'),
        ),
        migrations.AlterField(
            model_name='coursestudent',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master.course', verbose_name='درس'),
        ),
        migrations.AlterField(
            model_name='coursestudent',
            name='user',
            field=models.ForeignKey(limit_choices_to={'type': 's'}, on_delete=django.db.models.deletion.CASCADE, related_name='student_course', to=settings.AUTH_USER_MODEL, verbose_name='کاربر'),
        ),
        migrations.AlterField(
            model_name='exercise',
            name='author',
            field=models.ForeignKey(limit_choices_to={'type': 't'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='استاد'),
        ),
        migrations.AlterField(
            model_name='exercise',
            name='course',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='master.course', verbose_name='درس'),
        ),
        migrations.AlterField(
            model_name='exercise',
            name='date',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='تاریخ ایجاد'),
        ),
        migrations.AlterField(
            model_name='exercise',
            name='status',
            field=models.CharField(choices=[('e', 'بی پاسخ'), ('a', 'پاسخ داده شده')], default='e', max_length=30, verbose_name='وضعیت'),
        ),
        migrations.AlterField(
            model_name='exercise',
            name='tags',
            field=models.ManyToManyField(blank=True, to='master.Tag'),
        ),
        migrations.AlterField(
            model_name='exercise',
            name='title',
            field=models.CharField(max_length=100, unique=True, verbose_name='عنوان'),
        ),
        migrations.AlterField(
            model_name='post',
            name='postId',
            field=models.IntegerField(validators=[django.core.validators.MaxValueValidator(20000)], verbose_name='شماره پست'),
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(verbose_name='متن'),
        ),
        migrations.AlterField(
            model_name='postcomment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_post', to='master.post', verbose_name='پست'),
        ),
        migrations.AlterField(
            model_name='postcomment',
            name='text',
            field=models.TextField(verbose_name='متن'),
        ),
        migrations.AlterField(
            model_name='postcomment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='کاربر'),
        ),
        migrations.AlterField(
            model_name='postlike',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_like', to='master.post', verbose_name='پست'),
        ),
        migrations.AlterField(
            model_name='postlike',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='کاربر'),
        ),
        migrations.AlterField(
            model_name='user',
            name='city',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='شهر'),
        ),
        migrations.AlterField(
            model_name='user',
            name='date_joined',
            field=models.DateTimeField(auto_now_add=True, verbose_name='تاریخ عضویت'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=100, unique=True, verbose_name='ایمیل'),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='نام'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_superuser',
            field=models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='نام خانوادگی'),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(max_length=20, verbose_name='رمز عبور'),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.IntegerField(blank=True, null=True, verbose_name='شماره همراه'),
        ),
        migrations.AlterField(
            model_name='user',
            name='state',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='استان'),
        ),
        migrations.AlterField(
            model_name='user',
            name='type',
            field=models.CharField(choices=[('t', 'استاد'), ('s', 'دانشجو')], max_length=15, verbose_name='نقش'),
        ),
        migrations.AlterField(
            model_name='user',
            name='university',
            field=models.CharField(max_length=50, verbose_name='دانشگاه'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=20, unique=True, verbose_name='نام کاربری'),
        ),
        migrations.DeleteModel(
            name='ExerciseComment',
        ),
        migrations.DeleteModel(
            name='Identity',
        ),
        migrations.AddField(
            model_name='subject',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master.course', verbose_name='درس'),
        ),
        migrations.AddField(
            model_name='exerciseanswer',
            name='exercise',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master.exercise', verbose_name='تمرین'),
        ),
        migrations.AddField(
            model_name='exerciseanswer',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='دانشجو'),
        ),
        migrations.AddField(
            model_name='exercise',
            name='subject',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='master.subject', verbose_name='مبحث'),
        ),
    ]
