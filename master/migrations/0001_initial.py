# Generated by Django 3.2.4 on 2021-06-15 11:15

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
                ('email', models.EmailField(max_length=100, unique=True)),
                ('first_name', models.CharField(max_length=20)),
                ('last_name', models.CharField(max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to=master.models.user_avatar_directory_path, verbose_name='avatar')),
                ('university', models.CharField(max_length=50)),
                ('username', models.CharField(max_length=20, unique=True)),
                ('password', models.CharField(max_length=20)),
                ('type', models.CharField(choices=[('t', 'استاد'), ('s', 'دانشجو')], max_length=15)),
                ('phone', models.IntegerField()),
                ('state', models.CharField(max_length=30)),
                ('city', models.CharField(max_length=30)),
                ('code', models.IntegerField(blank=True, null=True, verbose_name='code')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'کاربران',
                'verbose_name_plural': 'کاربران',
                'ordering': ['-date_joined'],
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(max_length=1000)),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('end_date', models.DateTimeField()),
                ('exam_date', models.DateTimeField()),
                ('teacher', models.ForeignKey(limit_choices_to={'type': 't'}, on_delete=django.db.models.deletion.CASCADE, related_name='teacher_course', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(max_length=1000)),
                ('answer', models.FileField(null=True, upload_to='')),
                ('status', models.CharField(choices=[('e', 'Empty'), ('a', 'Answered')], max_length=30)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master.course')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('postId', models.IntegerField()),
                ('userId', models.IntegerField()),
                ('text', models.TextField()),
                ('file', models.FileField(blank=True, help_text='Image size should be less than 1.0\xa0MB', null=True, upload_to=master.models.post_image_directory_path, validators=[django.core.validators.FileExtensionValidator(['png', 'jpg', 'jpeg']), master.models.validate_image_size], verbose_name='آواتار')),
                ('time', models.DateTimeField()),
            ],
            options={
                'verbose_name': 'پست',
                'verbose_name_plural': 'پستها',
                'ordering': ['text'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=600)),
                ('link', models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='PostLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Date', models.DateTimeField()),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='postlike_post', to='master.post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PostComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('time', models.DateTimeField()),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_post', to='master.post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Identity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier_image', models.ImageField(blank=True, null=True, upload_to=master.models.user_identifier_image_directory_path, verbose_name='عکس احراز هویت')),
                ('request_time', models.DateTimeField(blank=True, null=True, verbose_name='زمان درخواست')),
                ('expire_time', models.DateTimeField(blank=True, null=True, verbose_name='زمان ابطال')),
                ('status', models.CharField(choices=[('2', 'احراز شده'), ('1', 'درخواست احراز'), ('3', 'احراز نشده')], default='3', max_length=1, verbose_name='وضعیت')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={
                'verbose_name': 'احراز هویت',
                'verbose_name_plural': 'احراز هویت',
                'ordering': ['-request_time'],
            },
        ),
        migrations.CreateModel(
            name='ExerciseComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(max_length=2000)),
                ('date', models.DateField(auto_now_add=True)),
                ('time', models.TimeField(auto_now_add=True)),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master.exercise')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.AddField(
            model_name='exercise',
            name='tags',
            field=models.ManyToManyField(to='master.Tag'),
        ),
        migrations.CreateModel(
            name='CourseStudent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master.course')),
                ('user', models.ForeignKey(limit_choices_to={'type': 's'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
