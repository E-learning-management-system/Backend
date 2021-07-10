from abc import ABC

from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    date_joined = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'university', 'type', 'first_name', 'last_name',
                  'phone',
                  'state', 'city',
                  'photo', 'date_joined']


TYPE_CHOICES = [
    ('t', 'استاد'),
    ('s', 'دانشجو'),
]


class SignupSerializer(serializers.Serializer, ABC):
    type = serializers.ChoiceField(TYPE_CHOICES)
    university = serializers.CharField(label='', write_only=True)
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

        user = User.objects.create_user(username, email, password, type, university)

        return user


class SigninSerializer(serializers.Serializer, ABC):
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


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'teacher', 'start_date', 'end_date', 'exam_date']


class CourseStudentSerializer(serializers.ModelSerializer):
    course = serializers.ReadOnlyField()

    class Meta:
        model = CourseStudent
        fields = ['user', 'course']


class PostSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['postId', 'poster', 'text', 'date', 'file', 'comments', 'likes']

    def get_likes(self, post):
        return PostLike.objects.filter(post=post).count()

    def get_comments(self, post):
        return PostComment.objects.filter(post=post).count()


class CommentSerializer(serializers.ModelSerializer):
    post = serializers.ReadOnlyField()
    user = serializers.ReadOnlyField()

    class Meta:
        model = PostComment
        fields = ['post', 'user', 'text', 'date']


class LikeSerializer(serializers.ModelSerializer):
    post = serializers.ReadOnlyField()
    user = serializers.ReadOnlyField()

    class Meta:
        model = PostLike
        fields = ['user', 'post', 'date']


class SubjectSerializer(serializers.ModelSerializer):
    course = serializers.ReadOnlyField()
    course_id = serializers.ReadOnlyField(source='course.id')

    class Meta:
        model = Subject
        fields = ['title', 'course', 'course_id']


class ExerciseSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    subject = serializers.ReadOnlyField()
    course = serializers.ReadOnlyField()

    class Meta:
        model = Exercise
        fields = ['id', 'course', 'subject', 'author', 'title', 'description', 'date', 'deadline']


class ExAnswerSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    exercise = serializers.ReadOnlyField()

    class Meta:
        model = ExerciseAnswer
        fields = ['id', 'user', 'exercise', 'text', 'date', 'time']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'title', 'link']
