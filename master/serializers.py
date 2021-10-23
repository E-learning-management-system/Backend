from django.contrib.auth import authenticate, password_validation
from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    date_joined = serializers.ReadOnlyField(label='تاریخ عضویت')
    email = serializers.ReadOnlyField(label='ایمیل')

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'university', 'type', 'name',
                  'bio', 'photo', 'date_joined']


TYPE_CHOICES = [
    ('t', 'استاد'),
    ('s', 'دانشجو'),
]


class SignupSerializer(serializers.Serializer):
    type = serializers.ChoiceField(TYPE_CHOICES, label='نقش')
    university = serializers.CharField(label='دانشگاه', write_only=True)
    email = serializers.EmailField(label='ایمیل', write_only=True)
    password = serializers.CharField(label='رمز عبور', max_length=128, write_only=True)
    password_confirmation = serializers.CharField(label='تکرار رمز عبور', max_length=128, write_only=True)
    token = serializers.CharField(label='توکن', read_only=True)

    def validate(self, attrs):
        type = attrs.get('type')
        university = attrs.get('university')
        email = attrs.get('email')
        password = attrs.get('password')
        password_confirmation = attrs.get('password_confirmation')

        if type and university and email and password and password_confirmation:
            user = authenticate(request=self.context.get('request'), type=type, university=university, email=email,
                                password=password)
            user1 = User.objects.filter(email=email)
            if user:
                raise serializers.ValidationError('کاربر موجود است!', code='conflict')
            if user1:
                raise serializers.ValidationError('این ایمیل موجود است!', code='conflict')
            if password != password_confirmation:
                raise serializers.ValidationError('رمز عبور با تکرارش یکسان نیست!', code='conflict')
            password_validation.validate_password(attrs['password'], self.context['request'].user)
        else:
            raise serializers.ValidationError('اطلاعات را به درستی وارد کنید!', code='authorization')

        return attrs

    def create(self, validated_data):
        type = validated_data['type']
        university = validated_data['university']
        email = validated_data['email']
        password = validated_data['password']

        user = User.objects.create_user(type, university, email, password)
        return user


class SigninSerializer(serializers.Serializer):
    email = serializers.CharField(label='ایمیل', write_only=True)
    password = serializers.CharField(label='رمز عبور', write_only=True)
    token = serializers.CharField(label='توکن', read_only=True)

    class Meta:
        model = User

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)
            if not user:
                raise serializers.ValidationError('کاربری با این اطلاعات موجود نیست!', code='authorization')
        else:
            raise serializers.ValidationError('اطلاعات را به درستی وارد کنید!', code='authorization')

        attrs['user'] = user
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(label='ایمیل', write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        if email:
            user = User.objects.filter(email=email)
            if user:
                user = user.first()
            if not user:
                raise serializers.ValidationError('کاربری با این اطلاعات موجود نیست!', code='authorization')
        else:
            raise serializers.ValidationError('ایمیل نمی تواند خالی باشد!', code='authorization')

        attrs['email'] = user.email
        return attrs


class Verification(serializers.Serializer):
    email = serializers.EmailField(label='ایمیل', write_only=True)
    code = serializers.CharField(label='کد یکبار مصرف', min_length=8, write_only=True)
    token = serializers.CharField(label='توکن', read_only=True)

    class Meta:
        model = User

    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('code')
        if email and code:
            user = User.objects.filter(email=email, code=code)
            if user:
                user = user.first()
            if not user:
                raise serializers.ValidationError('کد وارد شده صحیح نیست!', code='authorization')
        else:
            raise serializers.ValidationError('این فیلد نمی تواند خالی باشد!', code='authorization')

        attrs['user'] = user
        return attrs


class FPChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(label='رمز عبور حدید', max_length=128, required=True,
                                         write_only=True)
    new_password_confirmation = serializers.CharField(label='تکرار رمز عبور جدید', max_length=128,
                                                      required=True, write_only=True)

    def validate(self, data):
        if data['new_password'] != data['new_password_confirmation']:
            raise serializers.ValidationError('رمز عبور با تکرارش یکسان نیست!', code='conflict')
        password_validation.validate_password(data['new_password'], self.context['request'].user)
        return data

    def save(self, **kwargs):
        password = self.validated_data['new_password']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user


class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(label='رمز عبور', write_only=True)

    def validate_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('رمز عبور اشتباه است!')
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.is_active = False
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(label='رمز عبور قبلی', max_length=128, required=True,
                                         write_only=True)
    new_password = serializers.CharField(label='رمز عبور حدید', max_length=128, required=True,
                                         write_only=True)
    new_password_confirmation = serializers.CharField(label='تکرار رمز عبور جدید', max_length=128,
                                                      required=True, write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('رمز عبور قبلی اشتباه است!')
        return value

    def validate(self, data):
        if data['new_password'] != data['new_password_confirmation']:
            raise serializers.ValidationError('رمز عبور با تکرارش یکسان نیست!', code='conflict')
        password_validation.validate_password(data['new_password'], self.context['request'].user)
        return data

    def save(self, **kwargs):
        password = self.validated_data['new_password']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user


class Support(serializers.ModelSerializer):
    date = serializers.ReadOnlyField()

    class Meta:
        model = Support
        fields = ['id', 'email', 'title', 'description', 'date']


class CourseSerializer(serializers.ModelSerializer):
    teacher = serializers.ReadOnlyField(source='teacher.username')

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'teacher', 'start_date', 'end_date', 'exam_date']

    def validate(self, attrs):
        startdate = attrs.get('start_date')
        enddate = attrs.get('end_date')
        examdate = attrs.get('exam_date')

        if startdate > enddate:
            raise serializers.ValidationError('تاریخ پایان باید بعد از تاریخ آغاز باشد.')
        if examdate < startdate:
            raise serializers.ValidationError('تاریخ امتحان باید بعد از تاریخ آغاز باشد.')
        return attrs


class CourseRUDSerializer(serializers.ModelSerializer):
    teacher = serializers.ReadOnlyField(source='teacher.email')
    course_title = serializers.ReadOnlyField(source='course.title')

    class Meta:
        model = Course
        fields = ['id', 'course_title', 'teacher', 'description', 'start_date', 'end_date', 'exam_date']

    def validate(self, attrs):
        startdate = attrs.get('start_date')
        enddate = attrs.get('end_date')
        examdate = attrs.get('exam_date')

        if startdate > enddate:
            raise serializers.ValidationError('تاریخ پایان باید بعد از تاریخ آغاز باشد.')
        if examdate < startdate:
            raise serializers.ValidationError('تاریخ امتحان باید بعد از تاریخ آغاز باشد.')
        return attrs


class CourseStudentSerializer(serializers.ModelSerializer):
    course_id = serializers.ReadOnlyField(source='course.id')
    course_title = serializers.ReadOnlyField(source='course.title')
    course_teacher = serializers.ReadOnlyField(source='course.teacher.email')
    email = serializers.ReadOnlyField(source='user.email')
    user_id = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = CourseStudent
        fields = ['id', 'email', 'user_id', 'course_id', 'course_title', 'course_teacher']


class SubjectSerializer(serializers.ModelSerializer):
    course_id = serializers.ReadOnlyField(source='course.id')
    course_name = serializers.ReadOnlyField(source='course.title')
    teacher = serializers.ReadOnlyField(source='course.teacher.email')

    class Meta:
        model = Subject
        fields = ['id', 'title', 'course_name', 'course_id', 'teacher']


class PostSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()

    course_id = serializers.ReadOnlyField(source='course.id')
    course_title = serializers.ReadOnlyField(source='course.title')
    subject_id = serializers.ReadOnlyField(source='subject.id')
    subject_title = serializers.ReadOnlyField(source='subject.id')
    course_teacher = serializers.ReadOnlyField(source='course.teacher.email')
    user_id = serializers.ReadOnlyField(source='user.id')
    user_email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = Post
        fields = ['id', 'user_id', 'user_email', 'course_teacher', 'course_id', 'course_title', 'title',
                  'subject_id', 'subject_title', 'description', 'date', 'file', 'comments', 'likes']

    def get_likes(self, post):
        return PostLike.objects.filter(post=post).count()

    def get_comments(self, post):
        return PostComment.objects.filter(post=post).count()


class CommentSerializer(serializers.ModelSerializer):
    post_id = serializers.ReadOnlyField(source='post.id')
    user_email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = PostComment
        fields = ['id', 'post_id', 'user_email', 'text', 'date']


class LikeSerializer(serializers.ModelSerializer):
    post_id = serializers.ReadOnlyField(source='post.id')
    user = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = PostLike
        fields = ['id', 'user', 'post_id', 'date']


class ExerciseSerializer(serializers.ModelSerializer):
    teacher = serializers.ReadOnlyField(source='teacher.email')
    course_id = serializers.ReadOnlyField(source='course.id')
    course_title = serializers.ReadOnlyField(source='course.title')

    class Meta:
        model = Exercise
        fields = ['id', 'title', 'description', 'teacher', 'course_id', 'course_title',
                  'date', 'deadline', 'file']


class AnswerSerializer(serializers.ModelSerializer):
    exercise_id = serializers.ReadOnlyField(source='exercise.id')
    exercise_title = serializers.ReadOnlyField(source='exercise.title')
    user = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = Answer
        fields = ['id', 'exercise_id', 'exercise_title', 'user', 'description', 'date', 'file']
