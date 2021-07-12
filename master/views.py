from datetime import datetime
from django.core.mail import send_mail
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import generics, permissions, status

from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from .serializers import *


class Signup(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary='Create a new user',
        responses={
            201: OpenApiResponse(response=SignupSerializer, description='created'),
            400: OpenApiResponse(description='correctly fill the necessary fields')
        }
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        user = User.objects.get(type=serializer.validated_data['type'],
                                university=serializer.validated_data['university'],
                                email=serializer.validated_data['email'])
        mail = '{0}'.format(str(serializer.validated_data['email']))
        send_mail('سورن',
                  'به سورن خوش آمدید!',
                  'no-reply-khu@markop.ir',
                  [mail])
        token, create = Token.objects.get_or_create(user=user)
        data = {'token': token.key}
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class Signin(generics.GenericAPIView):
    serializer_class = SigninSerializer
    permissions = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, create = Token.objects.get_or_create(user=user)
        data = {'token': token.key}
        return Response(data)


class ForgotPassword(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permissions = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = 'Password : {0}'.format(str(serializer.validated_data['password']))
        mail = '{0}'.format(str(serializer.validated_data['email']))
        send_mail('سورن',
                  data,
                  'no-reply-khu@markop.ir',
                  [mail])
        return Response(status=status.HTTP_200_OK)


class profile(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class CourseList(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.type == 't':
            return Course.objects.filter(teacher=self.request.user)
        elif self.request.user.type == 's':
            return self.request.user.course_set.all()


class CourseCreate(generics.CreateAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_authentication(self, request):
        if self.request.user.type != 't':
            raise ValidationError('شما به این عمل دسترسی ندارید')

    def perform_create(self, serializer):
        """data = JSONParser().parse(self.request)
        newtitle = data['title']
        newdescription = data['description']
        startdate = data['start_date']
        enddate = data['end_date']
        examdate = data['exam_date']
        if startdate > enddate:
            raise ValidationError('تاریخ شروع درس باید پیش از تاریخ پایان آن باشد')
        elif examdate < startdate:
            raise ValidationError('تاریخ امتحان باید بعد از تاریخ شروع کلاس ها باشد')
        else:"""
        serializer.save(teacher=self.request.user)


class CourseRUD(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CourseRUDSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Course.objects.all()

    def delete(self, request, *args, **kwargs):
        course = Course.objects.filter(teacher=self.request.user, pk=self.kwargs['pk'])
        if self.request.user.type == 't':
            if course.exists():
                return self.destroy(request, *args, **kwargs)
            else:
                raise ValidationError('شما به این عمل دسترسی ندارید')
        else:
            raise ValidationError('شما به این عمل دسترسی ندارید')

    def perform_update(self, serializer):
        if self.request.user.type != 't':
            raise ValidationError('شما به این عمل دسترسی ندارید')


class CourseStudentList(generics.ListAPIView):
    serializer_class = CourseStudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_authentication(self, request):
        if self.request.user.type != 't':
            raise ValidationError('شما به این عمل دسترسی ندارید')

    def get_queryset(self):
        return CourseStudent.objects.filter(course=self.kwargs['pk'], course__teacher=self.request.user)


class CourseStudentCreate(generics.CreateAPIView):
    serializer_class = CourseStudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_authentication(self, request):
        if self.request.user.type != 't':
            raise ValidationError('Access Denied')

    def perform_create(self, serializer):
        course = Course.objects.get(pk=self.kwargs['pk'], teacher=self.request.user)
        if course:
            serializer.save(course=course)
        else:
            raise ValidationError('Access Denied')


class CourseStudentRD(generics.RetrieveDestroyAPIView):
    serializer_class = CourseStudentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = CourseStudent.objects.all()

    def perform_authentication(self, request):
        if self.request.user.type != 't':
            raise ValidationError('Access Denied')

    def delete(self, request, *args, **kwargs):
        student = CourseStudent.objects.filter(pk=kwargs['pk'], course__teacher=self.request.user)
        if student.exists():
            return self.destroy(self, request, *args, **kwargs)
        else:
            raise ValidationError('Access Denied')


class SubjectCreate(generics.CreateAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_authentication(self, request):
        if self.request.user.type != 't':
            raise ValidationError('شما به این عمل دسترسی ندارید')

    def perform_create(self, serializer):
        course = Course.objects.get(pk=self.kwargs['pk'], teacher=self.request.user)
        if course:
            serializer.save(course=course)
        else:
            raise ValidationError('Access Denied')


class SubjectList(generics.ListAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.type == 't':
            return Course.objects.get(pk=self.kwargs['pk'], teacher=self.request.user).subject_set.all()
        if self.request.user.type == 's':
            return self.request.user.course_set.get(pk=self.kwargs['pk']).subject_set.all()


class SubjectRUD(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Subject.objects.all()

    def delete(self, request, *args, **kwargs):
        if self.request.user.type != 't':
            raise ValidationError('شما به این عمل دسترسی ندارید')
        subject = Subject.objects.filter(pk=kwargs['pk'], course__teacher=self.request.user)
        if subject.exists():
            return self.destroy(request, *args, **kwargs)
        else:
            raise ValidationError('شما به این عمل دسترسی ندارید')

    def perform_update(self, serializer):
        if self.request.user.type != 't':
            raise ValidationError('شما به این عمل دسترسی ندارید')


class PostList(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.type == 't':
            return Course.objects.get(pk=self.kwargs['pk'], teacher=self.request.user).post_set.all()
        if self.request.user.type == 's':
            return self.request.user.course_set.get(pk=self.kwargs['pk']).post_set.all()


class PostRUD(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Post.objects.all()

    def delete(self, request, *args, **kwargs):
        post = Post.objects.filter(pk=kwargs['pk'], poster=self.request.user)
        if post.exists():
            return self.destroy(request, *args, **kwargs)
        else:
            raise ValidationError('شما به این عمل دسترسی ندارید')

    def perform_update(self, serializer):
        post = Post.objects.filter(pk=self.kwargs['pk'], poster=self.request.user)
        if not post:
            raise ValidationError('شما به این عمل دسترسی ندارید')


class PostCreate(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_authentication(self, request):
        if self.request.user.type == 't':
            if Course.objects.get(pk=self.kwargs['pk']).teacher != self.request.user:
                raise ValidationError('شما به این عمل دسترسی ندارید')
        elif self.request.user.type == 's':
            user = self.request.user.course_set.filter(pk=self.kwargs['pk'])
            if not user:
                raise ValidationError('شما به این عمل دسترسی ندارید')

    def perform_create(self, serializer):

        serializer.save(course=Course.objects.get(pk=self.kwargs['pk']), poster=self.request.user)


class LikeCreate(generics.CreateAPIView):
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        post = Post.objects.get(pk=self.kwargs['pk'])
        like = PostLike.objects.filter(post=post, user=self.request.user)
        if like.exists():
            raise ValidationError('شما قبلا این پست را لایک کرده اید')
        if not post:
            raise ValidationError('نتیجه ای یافت نشد')
        else:
            serializer.save(user=self.request.user, post=Post.objects.get(pk=self.kwargs['pk']))


class LikeList(generics.ListAPIView):
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PostLike.objects.filter(post=Post.objects.get(pk=self.kwargs['pk']))


class LikeDestroy(generics.DestroyAPIView):
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = PostLike.objects.all()

    def delete(self, request, *args, **kwargs):
        like = PostLike.objects.get(pk=self.kwargs['pk'], user=self.request.user)
        if like:
            return self.destroy(self, request, *args, **kwargs)
        else:
            raise ValidationError('Access Denied')


class CommentCreate(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_authentication(self, request):
        if self.request.user.type != 's':
            raise ValidationError('فقط دانشجویان میتوانند کامنت بگذارند')

    def perform_create(self, serializer):
        if self.request.user.type == 's':
            serializer.save(post=Post.objects.get(pk=self.kwargs['pk']), user=self.request.user)


class CommentList(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PostComment.objects.filter(post=Post.objects.get(pk=self.kwargs['pk']))


class CommentDelete(generics.DestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = PostComment.objects.all()

    def delete(self, request, *args, **kwargs):
        if self.request.user.type == 't':
            comment = PostComment.objects.get(pk=self.kwargs['pk'], post__course__teacher=self.request.user)
            if comment:
                return self.destroy(self, request, *args, **kwargs)
            else:
                raise ValidationError('Access Denied')
        elif self.request.user.type == 's':
            comment = PostComment.objects.get(pk=self.kwargs['pk'], user=self.request.user)
            if comment:
                return self.destroy(self, request, *args, **kwargs)
            else:
                raise ValidationError('Access Denied')


###########################################################################################
class ExerciseList(generics.ListAPIView):
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.type == 't':
            return Exercise.objects.filter(author=self.request.user)
        elif self.request.user.type == 's':
            return self.request.user.exercise_set.all()


class ExerciseCreate(generics.CreateAPIView):
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_authentication(self, request):
        if self.request.user.type != 't':
            raise serializers.ValidationError('شما به این عمل دسترسی ندارید')

    def perform_create(self, serializer):
        """data = JSONParser().parse(self.request)
        newtitle = data['title']
        newdescription = data['description']
        startdate = data['start_date']
        enddate = data['end_date']
        examdate = data['exam_date']
        if startdate > enddate:
            raise ValidationError('تاریخ شروع درس باید پیش از تاریخ پایان آن باشد')
        elif examdate < startdate:
            raise ValidationError('تاریخ امتحان باید بعد از تاریخ شروع کلاس ها باشد')
        else:"""
        serializer.save(author=self.request.user)


class ExerciseListCreate(generics.ListCreateAPIView):
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Exercise.objects.filter(author=self.request.user)

    def perform_create(self, serializer):
        if self.request.user.type == 't':
            serializer.save(author=self.request.user)
        else:
            raise serializers.ValidationError('فقظ اساتید قابلیت ایجاد به این عمل دسترسی دارند')


class ExerciseRUD(generics.RetrieveDestroyAPIView):
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.type == 't':
            return Exercise.objects.filter(author=self.request.user)


class ExerciseAnswerListCreate(generics.ListCreateAPIView):
    serializer_class = ExerciseAnswerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        exercise = Exercise.objects.get(pk=self.kwargs['pk'])
        if user.type == 's':
            if exercise.deadline > datetime.now():
                serializer.save(author=self.request.user, exercise=Exercise.objects.get(pk=self.kwargs['pk']))
            else:
                raise serializers.ValidationError('مهلت پاسخ دهی به اتمام رسیده است')

    def get_queryset(self):
        if self.request.user.type == 't':
            return ExerciseAnswer.objects.filter(exercise=Exercise.objects.get(pk=self.kwargs['pk']))


class ExerciseAnswerRUD(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExerciseAnswerSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ExerciseAnswer.objects.all()

    def delete(self, request, *args, **kwargs):
        if self.request.user.type != 't':
            raise serializers.ValidationError('شما به این عمل دسترسی ندارید')
        exerciseAnswer = ExerciseAnswer.objects.filter(pk=kwargs['pk'])
        if exerciseAnswer.exists():
            return self.destroy(request, *args, **kwargs)

    def perform_update(self, serializer):
        if self.request.user.type != 't':
            raise serializers.ValidationError('شما به این عمل دسترسی ندارید')
        serializer.save(author=self.request.user)


class ExerciseAnswerList(generics.ListAPIView):
    serializer_class = ExerciseAnswerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.type == 't':
            return ExerciseAnswer.objects.get(pk=self.kwargs['pk'], author=self.request.user).ExerciseAnswer_set.all()
        if self.request.user.type == 's':
            return self.request.user.course_set.get(pk=self.kwargs['pk']).subject_set.all()


class ExerciseAnswerCreate(generics.CreateAPIView):
    serializer_class = ExerciseAnswerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_authentication(self, request):
        if self.request.user.type != 't':
            raise serializers.ValidationError('شما به این عمل دسترسی ندارید')

    def perform_create(self, serializer):
        serializer.save(exercise=Exercise.objects.get(pk=self.kwargs['pk']))


class TagCreate(generics.CreateAPIView):
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_authentication(self, request):
        if self.request.user.type != 't':
            raise serializers.ValidationError('شما به این عمل دسترسی ندارید')

    def perform_create(self, serializer):
        serializer.save(exercise=Exercise.objects.get(pk=self.kwargs['pk']))


class TagList(generics.ListAPIView):
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.type == 't':
            return Exercise.objects.get(pk=self.kwargs['pk'], author=self.request.user).tag_set.all()
        if self.request.user.type == 's':
            return self.request.user.exercise_set.get(pk=self.kwargs['pk']).tag_set.all()


class TagRUD(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Tag.objects.all()

    def delete(self, request, *args, **kwargs):
        tag = Tag.objects.filter(pk=kwargs['pk'])
        if tag.exists():
            return self.destroy(request, *args, **kwargs)

    def perform_update(self, serializer):
        serializer.save()
