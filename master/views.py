from django.core.mail import send_mail
from django.db.models import Q
from django.utils.crypto import get_random_string
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import *
from . import permissions as p
from rest_framework.generics import get_object_or_404


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
        user1 = User.objects.filter(email=serializer.validated_data['email'])
        code = get_random_string(length=8, allowed_chars='1234567890')
        if user1:
            user1 = user1.first()
            user1.code = code
            user1.save()
        mail = '{0}'.format(str(serializer.validated_data['email']))
        data = 'به سورن خوش آمدید\nرمز یکبار مصرف : {0}'.format(str(code))
        send_mail('سورن',
                  data,
                  'no-reply-khu@markop.ir',
                  [mail])
        email = serializer.validated_data['email']
        return Response(email, status=status.HTTP_201_CREATED, headers=headers)


class SVerification(generics.UpdateAPIView):
    serializer_class = Verification

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if user:
            user.is_active = True
            user.save()
        token, create = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)


class Signin(generics.GenericAPIView):
    serializer_class = SigninSerializer
    permissions = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, create = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)


class ForgotPassword(generics.CreateAPIView):
    serializer_class = ForgotPasswordSerializer
    permissions = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(email=serializer.validated_data['email'])
        code = get_random_string(length=8, allowed_chars='1234567890')
        if user:
            user = user.first()
            user.code = code
            user.save()
        data = 'رمز یکبار مصرف : {0}'.format(str(code))
        mail = '{0}'.format(str(serializer.validated_data['email']))
        send_mail('سورن',
                  data,
                  'no-reply-khu@markop.ir',
                  [mail])
        email = serializer.validated_data['email']
        return Response(email)


class Verification(generics.UpdateAPIView):
    serializer_class = Verification

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, create = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)


class FPChangePassword(generics.UpdateAPIView):
    serializer_class = FPChangePasswordSerializer
    model = User
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if hasattr(user, 'auth_token'):
            user.auth_token.delete()
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)


class Profile(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class DeleteAccount(generics.UpdateAPIView):
    serializer_class = DeleteAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if hasattr(user, 'auth_token'):
            user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class ChangeEmail(generics.UpdateAPIView):
    serializer_class = ChangeEmail
    permissions_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        code = get_random_string(length=8, allowed_chars='1234567890')
        if user:
            user.code = code
            user.save()
        data = 'رمز یکبار مصرف : {0}'.format(str(code))
        mail = '{0}'.format(str(serializer.validated_data['new_email']))
        send_mail('سورن',
                  data,
                  'no-reply-khu@markop.ir',
                  [mail])
        email = serializer.validated_data['new_email']
        return Response(email)


class EmailVerification(generics.UpdateAPIView):
    serializer_class = EmailVerification
    model = User
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)


class ChangePassword(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if hasattr(user, 'auth_token'):
            user.auth_token.delete()
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)


class Support(generics.CreateAPIView):
    serializer_class = Support
    permissions = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CourseList(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Course.objects.filter(Q(teacher=self.request.user) | Q(student__in=[self.request.user])).distinct()


class CourseCreate(generics.CreateAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, p.IsTeacher]

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


class CourseRUD(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CourseRUDSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Course.objects.all()

    def perform_authentication(self, request):
        if (self.request.user.type == 's') and (self.request.method != 'GET'):
            raise ValidationError('شما به این عمل دسترسی ندارید')

    def delete(self, request, *args, **kwargs):
        course = get_object_or_404(Course, teacher=self.request.user, pk=self.kwargs['pk'])
        return self.destroy(request, *args, **kwargs)


class CourseStudentList(generics.ListAPIView):
    serializer_class = CourseStudentSerializer
    permission_classes = [permissions.IsAuthenticated, p.IsTeacher]

    def get_queryset(self):
        return CourseStudent.objects.filter(course=self.kwargs['pk'], course__teacher=self.request.user)


class CourseStudentCreate(generics.CreateAPIView):
    serializer_class = CourseStudentSerializer
    permission_classes = [permissions.IsAuthenticated, p.IsTeacher]

    def perform_create(self, serializer):
        course = get_object_or_404(Course, pk=self.kwargs['pk'], teacher=self.request.user)
        user = get_object_or_404(User, email=self.kwargs['email'], type='s')
        serializer.save(course=course, user=User.objects.get(email=self.kwargs['email']))


class CourseStudentRD(generics.RetrieveDestroyAPIView):
    serializer_class = CourseStudentSerializer
    permission_classes = [permissions.IsAuthenticated, p.IsTeacher]
    queryset = CourseStudent.objects.all()

    def delete(self, request, *args, **kwargs):
        student = get_object_or_404(CourseStudent, pk=kwargs['pk'], course__teacher=self.request.user)
        return self.destroy(self, request, *args, **kwargs)


class SubjectCreate(generics.CreateAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated, p.IsTeacher]

    def perform_create(self, serializer):
        course = get_object_or_404(Course, pk=self.kwargs['pk'], teacher=self.request.user)
        serializer.save(course=course)


class SubjectList(generics.ListAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.type == 't':
            return get_object_or_404(Course, pk=self.kwargs['pk'], teacher=self.request.user).subject_set.all()
        if self.request.user.type == 's':
            return self.request.user.course_set.get(pk=self.kwargs['pk']).subject_set.all()


class SubjectRD(generics.RetrieveDestroyAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Subject.objects.all()

    def delete(self, request, *args, **kwargs):
        if self.request.user.type != 't':
            raise ValidationError('شما به این عمل دسترسی ندارید')
        subject = get_object_or_404(Subject, pk=kwargs['pk'], course__teacher=self.request.user)
        return self.destroy(request, *args, **kwargs)


class PostList(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.type == 't':
            return get_object_or_404(Subject, pk=self.kwargs['pk'], course__teacher=self.request.user).post_set.all()
        if self.request.user.type == 's':
            return get_object_or_404(Subject, pk=self.kwargs['pk'],
                                     course__student__in=[self.request.user]).post_set.all()


class PostRD(generics.RetrieveDestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Post.objects.all()

    def delete(self, request, *args, **kwargs):
        post = Post.objects.filter(pk=kwargs['pk'], poster=self.request.user)
        if post.exists():
            return self.destroy(request, *args, **kwargs)
        else:
            raise ValidationError('شما به این عمل دسترسی ندارید')


class PostCreate(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_authentication(self, request):
        if self.request.user.type == 't':
            if get_object_or_404(Subject, pk=self.kwargs['pk']).course.teacher != self.request.user:
                raise ValidationError('شما به این عمل دسترسی ندارید')
        elif self.request.user.type == 's':
            subject = get_object_or_404(Subject, pk=self.kwargs['pk'])
            if subject.course not in self.request.user.course_set.all():
                raise ValidationError('شما به این عمل دسترسی ندارید')

    def perform_create(self, serializer):
        serializer.save(subject=get_object_or_404(Subject, pk=self.kwargs['pk']), user=self.request.user)


class LikeCreate(generics.CreateAPIView):
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        like = PostLike.objects.filter(post=post, user=self.request.user)
        if like.exists():
            raise ValidationError('شما قبلا این پست را لایک کرده اید')
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
        like = get_object_or_404(PostLike, pk=self.kwargs['pk'], user=self.request.user)


class CommentCreate(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.type == 't':
            post = Post.objects.get(pk=self.kwargs['pk'], subject__course__teacher=self.request.user)
            if post:
                serializer.save(post=post, user=self.request.user)
            else:
                raise ValidationError('شما به این عمل دسترسی ندارید')
        elif self.request.user.type == 's':
            post = Post.objects.get(pk=self.kwargs['pk']).subject.course.coursestudent_set.get(user=self.request.user)
            if post:
                serializer.save(post=post, user=self.request.user)
            else:
                raise ValidationError('شما به این عمل دسترسی ندارید')
        else:
            raise ValidationError('شما به این عمل دسترسی ندارید')


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
            comment = PostComment.objects.get(pk=self.kwargs['pk'], post__subject__course__teacher=self.request.user)
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

        else:
            raise ValidationError('شما به این عمل دسترسی ندارید')


class ExerciseList(generics.ListAPIView):
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.type == 't':
            course = Course.objects.get(pk=self.kwargs['pk'], teacher=self.request.user)
            if course:
                return Exercise.objects.filter(course=Course.objects.get(pk=self.kwargs['pk']))
            else:
                raise ValidationError('شما به این عمل دسترسی ندارید')

        elif self.request.user.type == 's':
            student = Course.objects.get(pk=self.kwargs['pk']).coursestudent_set.get(
                user=self.request.user)
            if student:
                return Exercise.objects.filter(course=Course.objects.get(pk=self.kwargs['pk']))
            else:
                raise ValidationError('شما به این عمل دسترسی ندارید')


class ExerciseCreate(generics.CreateAPIView):
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_authentication(self, request):
        if self.request.user.type != 't':
            raise ValidationError('شما به این عمل دسترسی ندارید')

    def perform_create(self, serializer):
        course = Course.objects.get(pk=self.kwargs['pk'])
        if course.teacher == self.request.user:
            serializer.save(course=course, teacher=self.request.user)
        else:
            raise ValidationError('شما به این عمل دسترسی ندارید')


class ExerciseRD(generics.RetrieveDestroyAPIView):
    serializer_class = ExerciseSerializer
    permission_classes = [IsAuthenticated]
    queryset = Exercise.objects.all()

    def perform_authentication(self, request):
        if (self.request.user.type != 't') and (self.request.method == 'DELETE'):
            raise ValidationError('فقط اساتید میتوانند تمرین را حذف کنند')

    def delete(self, request, *args, **kwargs):
        course = Exercise.objects.get(pk=self.kwargs['pk']).course

        if course.teacher == self.request.user:
            return self.destroy(self, request, *args, **kwargs)
        else:
            raise ValidationError('شما به این عمل دسترسی ندارید')


class AnswerList(generics.ListAPIView):
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_authentication(self, request):
        if self.request.user.type != 't':
            raise ValidationError('شما به این عمل دسترسی ندارید')

    def get_queryset(self):
        exercise = Exercise.objects.get(pk=self.kwargs['pk'], user=self.request.user)
        if exercise:
            return Answer.objects.filter(exercise=exercise)
        else:
            raise ValidationError('شما به این عمل دسترسی ندارید')


class AnswerCreate(generics.CreateAPIView):
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_authentication(self, request):
        if self.request.user.type != 's':
            raise ValidationError('شما به این عمل دسترسی ندارید')

    def perform_create(self, serializer):
        exercise = Exercise.objects.get(pk=self.kwargs['pk'])
        exerciseCourseStudent = CourseStudent.objects.filter(course=exercise.course)
        if self.request.user in exerciseCourseStudent:
            serializer.save(exercise=exercise, user=self.request.user)
        else:
            raise ValidationError('شما به این عمل دسترسی ندارید')


class AnswerRD(generics.RetrieveDestroyAPIView):
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticated]
    queryset = Answer.objects.all()

    def perform_authentication(self, request):
        if (self.request.user.type != 's') and (self.request.method == 'DELETE'):
            raise ValidationError('فقط دانشجویان میتوانند جواب تمرین را حذف کنند')

    def delete(self, request, *args, **kwargs):
        answer = Answer.objects.get(pk=self.kwargs['pk'])
        if answer.user == self.request.user:
            return self.destroy(self, request, *args, **kwargs)
        else:
            raise ValidationError('شما به این عمل دسترسی ندارید')


class StudentExerciseList(generics.ListAPIView):
    serializer_class = ExerciseSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def perform_authentication(self, request):
        if self.request.user.type != 's':
            raise ValidationError('فقط دانشجویان میتوانند تمارین خود را ببینند')

    def get_queryset(self):
        studentCourses = list(
            CourseStudent.objects.filter(user=self.request.user).values_list('course', flat=True).distinct())
        return Exercise.objects.filter(Q(course__in=studentCourses))


class TeacherExerciseList(generics.ListAPIView):
    serializer_class = ExerciseSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def perform_authentication(self, request):
        if self.request.user.type != 't':
            raise ValidationError('فقط اساتید میتوانند تمارین خود را ببینند')

    def get_queryset(self):
        return Exercise.objects.filter(user=self.request.user)
