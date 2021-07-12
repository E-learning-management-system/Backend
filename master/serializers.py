from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    date_joined = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'university', 'type', 'first_name', 'last_name',
                  'phone', 'state', 'city', 'photo', 'date_joined']


TYPE_CHOICES = [
    ('t', 'استاد'),
    ('s', 'دانشجو'),
]


class SignupSerializer(serializers.Serializer):
    type = serializers.ChoiceField(TYPE_CHOICES, label='نقش')
    university = serializers.CharField(label='دانشگاه', write_only=True)
    email = serializers.EmailField(label='ایمیل', write_only=True)
    username = serializers.CharField(label='نام کاربری', write_only=True)
    password = serializers.CharField(label='رمز عبور', min_length=4,
                                     write_only=True, help_text='رمز عبور باید حداقل 4 رقمی باشد')
    token = serializers.CharField(label='توکن', read_only=True)

    def validate(self, attrs):
        type = attrs.get('type')
        university = attrs.get('university')
        email = attrs.get('email')
        username = attrs.get('username')
        password = attrs.get('password')
        if type and university and email and username and password:
            user = authenticate(request=self.context.get('request'), type=type, university=university, email=email,
                                username=username, password=password)
            if user:
                raise serializers.ValidationError('کاربر موجود است!', code='conflict')
        else:
            raise serializers.ValidationError('اطلاعات را به درستی وارد کنید!', code='authorization')

        return attrs

    def create(self, validated_data):
        type = validated_data['type']
        university = validated_data['university']
        email = validated_data['email']
        username = validated_data['username']
        password = validated_data['password']

        user = User.objects.create_user(username, type, university, email, password)
        return user


class SigninSerializer(serializers.Serializer):
    username = serializers.CharField(label='نام کاربری', write_only=True)
    password = serializers.CharField(label='رمز عبور', min_length=4,
                                     write_only=True, help_text='رمز عبور باید حداقل 4 رقمی باشد')
    token = serializers.CharField(label='توکن', read_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)
            if not user:
                raise serializers.ValidationError('کاربری با این اطلاعات موجود نیست!', code='authorization')
        else:
            raise serializers.ValidationError('اطلاعات را به درستی وارد کنید!', code='authorization')

        attrs['user'] = user
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(label='ایمیل', write_only=True)
    password = serializers.CharField(read_only=True)

    def check(self, attrs):
        email = attrs.get('email')
        if email:
            user = User.objects.filter(email)
            if user.exist():
                user = user.first()
            if not user:
                raise serializers.ValidationError('کاربری با این اطلاعات موجود نیست!', code='authorization')
        else:
            raise serializers.ValidationError('ایمیل نمی تواند خالی باشد!', code='authorization')

        attrs['user'] = user
        return user


class CourseSerializer(serializers.ModelSerializer):
    teacher = serializers.ReadOnlyField(source='teacher.username')

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'teacher', 'start_date', 'end_date', 'exam_date']


class CourseRUDSerializer(serializers.ModelSerializer):
    teacher = serializers.ReadOnlyField(source='teacher.username')
    course_title = serializers.ReadOnlyField(source='course.title')

    class Meta:
        model = Course
        fields = ['id', 'course_title', 'teacher', 'description', 'start_date', 'end_date', 'exam_date']


class CourseStudentSerializer(serializers.ModelSerializer):
    course_id = serializers.ReadOnlyField(source='course.id')
    course_title = serializers.ReadOnlyField(source='course.title')
    course_teacher = serializers.ReadOnlyField(source='course.teacher.username')
    user = serializers.ReadOnlyField(source='user.username')
    user_id = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = CourseStudent
        fields = ['id', 'user', 'user_id', 'course_id', 'course_title', 'course_teacher']


class PostSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()

    course_id = serializers.ReadOnlyField(source='course.id')
    course_title = serializers.ReadOnlyField(source='course.title')
    course_teacher = serializers.ReadOnlyField(source='course.teacher.username')
    poster_id = serializers.ReadOnlyField(source='poster.id')
    poster_username = serializers.ReadOnlyField(source='poster.username')

    class Meta:
        model = Post
        fields = ['id', 'poster_id', 'poster_username', 'course_teacher', 'course_id', 'course_title', 'text', 'date',
                  'file', 'comments',
                  'likes']

    def get_likes(self, post):
        return PostLike.objects.filter(post=post).count()

    def get_comments(self, post):
        return PostComment.objects.filter(post=post).count()


class CommentSerializer(serializers.ModelSerializer):
    post_id = serializers.ReadOnlyField(source='post.id')
    user_username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = PostComment
        fields = ['id', 'post_id', 'user_username', 'text', 'date']


class LikeSerializer(serializers.ModelSerializer):
    post_id = serializers.ReadOnlyField(source='post.id')
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = PostLike
        fields = ['id', 'user', 'post_id', 'date']


class SubjectSerializer(serializers.ModelSerializer):
    course_id = serializers.ReadOnlyField(source='course.id')
    course_name = serializers.ReadOnlyField(source='course.title')
    teacher = serializers.ReadOnlyField(source='course.teacher.username')

    class Meta:
        model = Subject
        fields = ['id', 'title', 'course_name', 'course_id', 'teacher']


############################################################################################
class ExerciseSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    subject = serializers.ReadOnlyField()
    course = serializers.ReadOnlyField()

    class Meta:
        model = Exercise
        fields = ['id', 'title', 'description', 'author', 'status', 'date', 'deadline', 'tags', 'file', 'course', 'subject']


class ExerciseAnswerSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    exercise = serializers.ReadOnlyField()

    class Meta:
        model = ExerciseAnswer
        fields = ['id', 'user', 'exercise', 'file', 'date']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'title', 'link']
