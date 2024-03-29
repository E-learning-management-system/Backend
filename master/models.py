from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin, AbstractUser
from django.db import models
from django.core.validators import FileExtensionValidator, ValidationError
from django.conf import settings
from django.template.defaultfilters import filesizeformat


def user_photo_directory_path(instance, filename):
    return 'user/{0}/photo/{1}'.format(str(instance.email), filename)


def post_image_directory_path(instance, filename):
    return 'user/{0}/post/{1}'.format(str(instance.user.email), filename)


def exercise_image_directory_path(instance, filename):
    return 'user/{0}/exercise/{1}'.format(str(instance.teacher.email), filename)


def exercise_ans_image_directory_path(instance, filename):
    return 'user/{0}/exercise_ans/{1}'.format(str(instance.user.email), filename)


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

    def create_user(self, type=None, university=None, email=None, password=None):
        if not type:
            raise ValueError('Users must choose a type')
        if not university:
            raise ValueError('Users must have a university')
        if not email:
            raise ValueError('Users must have an email')
        if not password:
            raise ValueError('Users must have a password')

        user = self.model(
            type=type,
            university=university,
            email=email
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email')
        if not password:
            raise ValueError('Users must have a password')

        user = self.model(
            email=email,
        )
        user.set_password(password)
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user


class User(PermissionsMixin, AbstractBaseUser):
    VALID_PHOTO_EXTENTION = ['jpg', 'png', 'jpeg']

    name = models.CharField(verbose_name="نام", blank=True, null=True, max_length=20)
    university = models.CharField(verbose_name="دانشگاه", max_length=50, null=True, blank=True)
    email = models.EmailField(verbose_name="ایمیل", unique=True, max_length=100, null=True, blank=True)
    password = models.TextField(verbose_name="رمز عبور", max_length=2000)
    type = models.CharField(verbose_name="نقش", max_length=1, choices=TYPE_CHOICES, null=True, blank=True)
    is_staff = models.BooleanField(verbose_name='کارمند', default=False)
    is_superuser = models.BooleanField(verbose_name='ابرکاربر', default=False)
    is_active = models.BooleanField(verbose_name='فعال', default=False)
    code = models.IntegerField(verbose_name="کد یکبار مصرف", null=True, blank=True)
    bio = models.CharField(verbose_name="بیو", null=True, max_length=30, blank=True)
    photo = models.ImageField(verbose_name="تصویر پروفایل",
                              validators=[FileExtensionValidator(VALID_PHOTO_EXTENTION), validate_image_size],
                              upload_to=user_photo_directory_path, null=True,
                              blank=True)
    last_login = models.DateTimeField(verbose_name="آخرین ورود", null=True, blank=True, auto_now_add=True)
    date_joined = models.DateTimeField(verbose_name="تاریخ عضویت", auto_now_add=True)
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'
    objects = UserManager()

    def __str__(self):
        if self.name is not None:
            return str(self.name)
        else:
            return str(self.email)

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
        ordering = ['-id']


class Support(models.Model):
    email = models.EmailField(verbose_name='ایمیل')
    title = models.CharField(verbose_name='موضوع', max_length=50)
    description = models.TextField(verbose_name='متن پیام', max_length=2000)
    date = models.DateTimeField(verbose_name='تاریخ', auto_now_add=True, null=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'پشتیبانی'
        verbose_name_plural = 'پشتیبانی ها'
        ordering = ['-id']


class Course(models.Model):
    title = models.CharField(verbose_name='عنوان', max_length=255)
    description = models.TextField(verbose_name='توضیحات', max_length=1000, blank=True, null=True)
    teacher = models.ForeignKey(User, verbose_name='استاد', related_name='teacher_course', on_delete=models.CASCADE,
                                limit_choices_to={'type': 't'})
    start_date = models.DateField(verbose_name='تاریخ آغاز', default=None)
    end_date = models.DateField(verbose_name='تاریخ پایان')
    exam_date = models.DateTimeField(verbose_name='تاریخ امتحان')
    student = models.ManyToManyField(User, verbose_name='دانشجویان', through='CourseStudent', blank=True)

    def __str__(self):
        if self.teacher.name is not None:
            return str(self.title) + ' ' + str(self.teacher.name)
        else:
            return str(self.title) + ' ' + str(self.teacher)

    class Meta:
        ordering = ['-id']
        verbose_name = 'درس'
        verbose_name_plural = 'درس ها'


class CourseStudent(models.Model):
    course = models.ForeignKey(Course, verbose_name='درس', on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='کاربر', related_name='student_course', on_delete=models.CASCADE,
                             limit_choices_to={'type': 's'})

    def __str__(self):
        if self.user.name is not None:
            return str(self.user.name)
        else:
            return str(self.user.email)

    class Meta:
        ordering = ['-id']
        verbose_name = 'دانشجو'
        verbose_name_plural = 'دانشجویان'


class Subject(models.Model):
    title = models.CharField(verbose_name='عنوان', max_length=100)
    course = models.ForeignKey(Course, verbose_name='درس', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-id']
        verbose_name = 'مبحث'
        verbose_name_plural = 'مباحث'


class Post(models.Model):
    VALID_AVATAR_EXTENSION = ['png', 'jpg', 'jpeg']
    subject = models.ForeignKey(Subject, verbose_name='مبحث', on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, verbose_name='کاربر', blank=True, null=True, related_name='post_user',
                             on_delete=models.CASCADE)
    title = models.CharField(max_length=50, verbose_name='موضوع', null=True, blank=True, default=None)
    description = models.TextField(verbose_name='متن')
    date = models.DateTimeField(verbose_name='تاریخ', auto_now_add=True, null=True)
    file = models.FileField(upload_to=post_image_directory_path,default=None, null=True, blank=True,
                            validators=[FileExtensionValidator(VALID_AVATAR_EXTENSION), validate_image_size],
                            verbose_name='فایل',

                            help_text='Image size should be less than {0}'.format(
                                filesizeformat(settings.MAX_UPLOAD_IMAGE_SIZE))
                            )
    savedby = models.ManyToManyField(User, verbose_name='ذخیره شده توسط: ', blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-id']
        verbose_name = 'پست'
        verbose_name_plural = 'پست ها'


class PostComment(models.Model):
    post = models.ForeignKey(Post, verbose_name='پست', on_delete=models.CASCADE, related_name='comment_post')
    user = models.ForeignKey(User, verbose_name='کاربر', on_delete=models.CASCADE)
    text = models.TextField(verbose_name='متن')
    date = models.DateTimeField(verbose_name='ایجاد شده در: ', auto_now_add=True, null=True)

    class Meta:
        ordering = ['-id']
        verbose_name = 'کامنت'
        verbose_name_plural = 'کامنت ها'


class PostLike(models.Model):
    user = models.ForeignKey(User, verbose_name='کاربر', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, verbose_name='پست', on_delete=models.CASCADE, related_name='post_like')
    date = models.DateTimeField(verbose_name='ایجاد شده در: ', auto_now_add=True, null=True)

    class Meta:
        verbose_name = 'لایک'
        verbose_name_plural = 'لایک ها'
        ordering = ['-id']


class Exercise(models.Model):
    VALID_AVATAR_EXTENSION = ['png', 'jpg', 'jpeg']
    title = models.CharField(max_length=100, verbose_name='عنوان', unique=True)
    description = models.TextField(max_length=1000)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='استاد', limit_choices_to={'type': 't'})
    date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد', null=True)
    deadline = models.DateTimeField(verbose_name='مهلت تحویل', null=True)
    course = models.ForeignKey(Course, verbose_name='درس', on_delete=models.CASCADE, null=True)
    file = models.FileField(upload_to=exercise_image_directory_path, null=True, blank=True,
                            validators=[FileExtensionValidator(VALID_AVATAR_EXTENSION), validate_image_size],
                            verbose_name='فایل',
                            help_text='Image size should be less than {0}'.format(
                                filesizeformat(settings.MAX_UPLOAD_IMAGE_SIZE))
                            )

    class Meta:
        ordering = ['-id']
        verbose_name = 'تمرین'
        verbose_name_plural = 'تمرین ها'

    def __str__(self):
        return self.title


class Answer(models.Model):
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
        ordering = ['-id']
        verbose_name = 'پاسخ'
        verbose_name_plural = 'پاسخ ها'

    def __str__(self):
        return '{0} on {1}'.format(self.user, self.date)
