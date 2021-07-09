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