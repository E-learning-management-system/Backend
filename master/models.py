from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin, AbstractUser
from django.db import models
from django.core.validators import FileExtensionValidator, ValidationError
from django.conf import settings
from django.template.defaultfilters import filesizeformat


def user_photo_directory_path(instance, filename):
    return 'user/{0}/photo/{1}'.format(str(instance.user.username), filename)


def post_image_directory_path(instance, filename):
    return 'user/{0}/post/{1}'.format(str(instance.poster.username), filename)


def exercise_image_directory_path(instance, filename):
    return 'user/{0}/exercise/{1}'.format(str(instance.poster.username), filename)


def exercise_ans_image_directory_path(instance, filename):
    return 'user/{0}/exercise_ans/{1}'.format(str(instance.poster.username), filename)


def validate_image_size(image):
    filesize = image.size
    if filesize > int(settings.MAX_UPLOAD_IMAGE_SIZE):
        raise ValidationError('حداکثر سایز عکس باید {} باشد'.format((filesizeformat(settings.MAX_UPLOAD_IMAGE_SIZE))))


TYPE_CHOICES = [
    ('a', 'ادمین'),
    ('t', 'استاد'),
    ('s', 'دانشجو')
]


class UserManager(BaseUserManager):

    def create_user(self, username, type=None, university=None, email=None, password=None):
        if not username:
            raise ValueError('Users must have a username')
        if not university:
            raise ValueError('Users must have a university')
        if not email:
            raise ValueError('Users must have an email')
        if not password:
            raise ValueError('Users must have a password')

        user = self.model(
            username=username,
            type=type,
            university=university,
            email=email
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None):
        if not username:
            raise ValueError('Users must have a username')
        if not password:
            raise ValueError('Users must have a password')

        user = self.model(
            username=username,
        )
        user.set_password(password)
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(PermissionsMixin, AbstractBaseUser):
    VALID_PHOTO_EXTENTION = ['jpg', 'png', 'jpeg']

    first_name = models.CharField(verbose_name="نام", blank=True, null=True, max_length=20)
    last_name = models.CharField(verbose_name="نام خانوادگی", blank=True, null=True, max_length=20)
    university = models.CharField(verbose_name="دانشگاه", max_length=50, null=True, blank=True)
    email = models.EmailField(verbose_name="ایمیل", unique=True, max_length=100, null=True, blank=True)
    username = models.CharField(verbose_name="نام کاربری", unique=True, max_length=20)
    password = models.TextField(verbose_name="رمز عبور", max_length=2000)
    type = models.CharField(verbose_name="نقش", max_length=1, choices=TYPE_CHOICES, null=True, blank=True)
    is_active = models.BooleanField(verbose_name='فعال', default=True)
    is_staff = models.BooleanField(verbose_name='کارمند', default=False)
    is_superuser = models.BooleanField(verbose_name='ابرکاربر', default=False)
    phone = models.IntegerField(verbose_name="شماره همراه", null=True, blank=True)
    state = models.CharField(verbose_name="استان", null=True, max_length=30, blank=True)
    city = models.CharField(verbose_name="شهر", null=True, max_length=30, blank=True)
    photo = models.ImageField(verbose_name="تصویر پروفایل",
                              validators=[FileExtensionValidator(VALID_PHOTO_EXTENTION), validate_image_size],
                              upload_to=user_photo_directory_path, null=True,
                              blank=True)
    date_joined = models.DateTimeField(verbose_name="تاریخ عضویت", auto_now_add=True)
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'username'
    objects = UserManager()

    def __str__(self):
        if (self.first_name is not None) and (self.last_name is not None):
            return str(self.first_name + ' ' + self.last_name)
        else:
            return str(self.username)

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
        ordering = ['username']


class Course(models.Model):
    title = models.CharField(verbose_name='عنوان', max_length=255)
    description = models.TextField(verbose_name='توضیحات', max_length=1000, blank=True, null=True)
    teacher = models.ForeignKey(User, verbose_name='استاد', related_name='teacher_course', on_delete=models.CASCADE,
                                limit_choices_to={'type': 't'})
    start_date = models.DateTimeField(verbose_name='تاریخ آغاز', default=None)
    end_date = models.DateTimeField(verbose_name='تاریخ پایان')
    exam_date = models.DateTimeField(verbose_name='تاریخ امتحان')
    student = models.ManyToManyField(User, verbose_name='دانشجویان', through='CourseStudent', blank=True)

    def __str__(self):
        if self.teacher.last_name is not None:
            return str(self.title) + ' ' + str(self.teacher.last_name)
        else:
            return str(self.title) + ' ' + str(self.teacher)

    class Meta:
        ordering = ['-title']
        verbose_name = 'درس'
        verbose_name_plural = 'درس ها'


class CourseStudent(models.Model):
    course = models.ForeignKey(Course, verbose_name='درس', on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='کاربر', related_name='student_course', on_delete=models.CASCADE,
                             limit_choices_to={'type': 's'})

    def __str__(self):
        if (self.user.first_name is not None) and (self.user.last_name is not None):
            return str(self.user.first_name + ' ' + self.user.last_name)
        else:
            return str(self.user.username)

    class Meta:
        verbose_name = 'دانشجو'
        verbose_name_plural = 'دانشجویان'


class Post(models.Model):
    VALID_AVATAR_EXTENSION = ['png', 'jpg', 'jpeg']
    course = models.ForeignKey(Course, verbose_name='درس', on_delete=models.CASCADE, default=None)
    poster = models.ForeignKey(User, verbose_name='کاربر', blank=True, null=True, related_name='post_user',
                               on_delete=models.CASCADE)
    text = models.TextField(verbose_name='متن')
    date = models.DateTimeField(verbose_name='تاریخ', auto_now_add=True, null=True)
    file = models.FileField(upload_to=post_image_directory_path, null=True, blank=True,
                            validators=[FileExtensionValidator(VALID_AVATAR_EXTENSION), validate_image_size],
                            verbose_name='فایل',

                            help_text='Image size should be less than {0}'.format(
                                filesizeformat(settings.MAX_UPLOAD_IMAGE_SIZE))
                            )

    def __str__(self):
        return str(self.postId)

    class Meta:
        ordering = ['-date']
        verbose_name = 'پست'
        verbose_name_plural = 'پست ها'


class PostComment(models.Model):
    post = models.ForeignKey(Post, verbose_name='پست', on_delete=models.CASCADE, related_name='comment_post')
    user = models.ForeignKey(User, verbose_name='کاربر', on_delete=models.CASCADE)
    text = models.TextField(verbose_name='متن')
    date = models.DateTimeField(verbose_name='ایجاد شده در: ', auto_now_add=True, null=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'کامنت'
        verbose_name_plural = 'کامنت ها'


class PostLike(models.Model):
    user = models.ForeignKey(User, verbose_name='کاربر', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, verbose_name='پست', on_delete=models.CASCADE, related_name='post_like')
    date = models.DateTimeField(verbose_name='ایجاد شده در: ', auto_now_add=True, null=True)

    class Meta:
        verbose_name = 'لایک'
        verbose_name_plural = 'لایک ها'
        ordering = ['-date']


class Subject(models.Model):
    title = models.CharField(verbose_name='عنوان', max_length=100)
    course = models.ForeignKey(Course, verbose_name='درس', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'مبحث'
        verbose_name_plural = 'مباحث'


class Exercise(models.Model):
    VALID_AVATAR_EXTENSION = ['png', 'jpg', 'jpeg']
    title = models.CharField(max_length=100, verbose_name='عنوان', unique=True)
    description = models.TextField(max_length=1000)
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='استاد', limit_choices_to={'type': 't'})
    date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد', null=True)
    deadline = models.DateTimeField(verbose_name='مهلت تحویل', null=True)
    tags = models.ManyToManyField('Tag', blank=True)
    course = models.ForeignKey(Course, verbose_name='درس', on_delete=models.CASCADE, null=True)
    subject = models.ForeignKey(Subject, verbose_name='مبحث', on_delete=models.CASCADE, null=True)
    file = models.FileField(upload_to=exercise_image_directory_path, null=True, blank=True,
                            validators=[FileExtensionValidator(VALID_AVATAR_EXTENSION), validate_image_size],
                            verbose_name='فایل',
                            help_text='Image size should be less than {0}'.format(
                                filesizeformat(settings.MAX_UPLOAD_IMAGE_SIZE))
                            )

    class Meta:
        ordering = ['-date']
        verbose_name = 'تمرین'
        verbose_name_plural = 'تمرین ها'

    def __str__(self):
        return self.title


class ExerciseAnswer(models.Model):
    VALID_AVATAR_EXTENSION = ['png', 'jpg', 'jpeg']
    exercise = models.ForeignKey('Exercise', verbose_name='تمرین', on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='دانشجو', on_delete=models.CASCADE)
    description = models.TextField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True, null=True, verbose_name='تاریخ بارگزاری')
    file = models.FileField(upload_to=exercise_ans_image_directory_path, null=True, blank=True,
                            validators=[FileExtensionValidator(VALID_AVATAR_EXTENSION), validate_image_size],
                            verbose_name='فایل',
                            help_text='Image size should be less than {0}'.format(
                                filesizeformat(settings.MAX_UPLOAD_IMAGE_SIZE))
                            )

    class Meta:
        ordering = ['-date']
        verbose_name = 'پاسخ'
        verbose_name_plural = 'پاسخ ها'

    def __str__(self):
        return '{0} on {1}'.format(self.user, self.date)


class Tag(models.Model):
    title = models.CharField(max_length=600)
    link = models.CharField(max_length=1000)

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = 'تگ'
        verbose_name_plural = 'تگ ها'
