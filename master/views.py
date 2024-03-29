from django.contrib.auth.models import update_last_login
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponse
from django.utils.crypto import get_random_string
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *
from . import permissions as p
from rest_framework.generics import get_object_or_404
from django.template.loader import render_to_string


class Signup(generics.CreateAPIView):
    serializer_class = SignupSerializer

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
        user = User.objects.filter(email=serializer.validated_data['email'])
        code = get_random_string(length=8, allowed_chars='1234567890')
        if user:
            user = user.first()
            user.code = code
            user.save()
        mail = '{0}'.format(str(serializer.validated_data['email']))
        msg_html = render_to_string('Email_Message.html', {'Verification_Code': code})
        send_mail('سورن',
                  msg_html,
                  'no-reply-khu@markop.ir',
                  [mail], html_message=msg_html)
        email = serializer.validated_data['email']
        return Response(email, status=status.HTTP_201_CREATED, headers=headers)


class SVerification(generics.UpdateAPIView):
    serializer_class = Verification

    def put(self, request, *args, **kwargs):
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

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        update_last_login(None, user)
        token, create = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)


class ForgotPassword(generics.CreateAPIView):
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(email=serializer.validated_data['email'])
        code = get_random_string(length=8, allowed_chars='1234567890')
        if user:
            user = user.first()
            user.code = code
            user.save()
        msg_html = render_to_string('Email_Message.html', {'Verification_Code': code})
        mail = '{0}'.format(str(serializer.validated_data['email']))
        send_mail('سورن',
                  msg_html,
                  'no-reply-khu@markop.ir',
                  [mail], html_message=msg_html)
        email = serializer.validated_data['email']
        return Response(email)


class Verification(generics.UpdateAPIView):
    serializer_class = Verification

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, create = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)


class FPChangePassword(generics.UpdateAPIView):
    serializer_class = FPChangePasswordSerializer
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


class UserProfile(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()

    def get_object(self):
        return get_object_or_404(User, email=self.kwargs['email'])


class DeleteAccount(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        user.delete()
        return Response(status=status.HTTP_200_OK)


class ChangeEmail(generics.UpdateAPIView):
    serializer_class = ChangeEmail
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        code = get_random_string(length=8, allowed_chars='1234567890')
        if user:
            user.code = code
            user.save()
        msg_html = render_to_string('Email_Message.html', {'Verification_Code': code})
        mail = '{0}'.format(str(serializer.validated_data['new_email']))
        send_mail('سورن',
                  msg_html,
                  'no-reply-khu@markop.ir',
                  [mail], html_message=msg_html)
        email = serializer.validated_data['new_email']
        return Response(email)


class EmailVerification(generics.UpdateAPIView):
    serializer_class = EmailVerification
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)


class ChangePassword(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
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

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 5


class CommentSetPagination(PageNumberPagination):
    page_size = 4
    page_query_param = 'page_size'
    max_page_size = 4


class CourseList(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['=title']
    pagination_class = LargeResultsSetPagination

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
        if self.request.method != 'GET':
            get_object_or_404(User, email=self.request.user.email, type='t')

    def delete(self, request, *args, **kwargs):
        course = get_object_or_404(Course, teacher=self.request.user, pk=self.kwargs['pk'])
        return self.destroy(request, *args, **kwargs)


class CourseStudentList(generics.ListAPIView):
    serializer_class = CourseStudentSerializer
    permission_classes = [permissions.IsAuthenticated, p.IsTeacher]
    search_fields = ['=user__name']
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        return CourseStudent.objects.filter(course=self.kwargs['pk'], course__teacher=self.request.user)


class CourseStudentCreate(generics.CreateAPIView):
    serializer_class = CourseStudentSerializer
    permission_classes = [permissions.IsAuthenticated, p.IsTeacher]

    def post(self, request, *args, **kwargs):
        course = get_object_or_404(Course, pk=self.kwargs['pk'], teacher=self.request.user)
        user = User.objects.filter(email=self.kwargs['email'])
        if not user.exists():
            mail = '{0}'.format(self.kwargs['email'])
            data = 'با سلام شما در درس {0} استاد {1} عضو هستید اما در سامانه سورن ثبت نام نکرده اید.'.format(
                course.title, course.teacher.name)
            send_mail('سورن',
                      data,
                      'no-reply-khu@markop.ir',
                      [mail])
            return Response('کاربر موجود نیست. از طریق ایمیل به ایشان اطلاع داده خواهد شد', status=400)
        if user.first().type == 't':
            return Response('ایمیل وارد شده باید متعلق به یک دانشجو باشد', status=400)
        if CourseStudent.objects.filter(course=course, user=user.first()).exists():
            return Response('این دانشجو قبلا اضافه شده است', status=400)
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)

    def perform_create(self, serializer):
        course = get_object_or_404(Course, pk=self.kwargs['pk'], teacher=self.request.user)
        user = User.objects.filter(email=self.kwargs['email'])
        serializer.save(course=course, user=user.first())


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


class AllSubjectList(generics.ListAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        if self.request.user.type == 't':
            return Subject.objects.filter(course__teacher=self.request.user)
        elif self.request.user.type == 's':
            return Subject.objects.filter(course__coursestudent__user__in=[self.request.user])


class SubjectList(generics.ListAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['=title']
    pagination_class = LargeResultsSetPagination

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
            return Response('شما به این عمل دسترسی ندارید', status=403)
        subject = get_object_or_404(Subject, pk=kwargs['pk'], course__teacher=self.request.user)
        return self.destroy(request, *args, **kwargs)


class PostList(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LargeResultsSetPagination

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
        post = Post.objects.filter(pk=kwargs['pk'], user=self.request.user)
        if post.exists():
            return self.destroy(request, *args, **kwargs)
        else:
            return Response('شما به این عمل دسترسی ندارید', status=403)


class PostCreate(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        subject = get_object_or_404(Subject, pk=self.kwargs['pk'])
        serializer.save(subject=subject, user=self.request.user)

    def post(self, request, *args, **kwargs):
        if self.request.user.type == 't':
            if get_object_or_404(Subject, pk=self.kwargs['pk']).course.teacher != self.request.user:
                return Response('شما به این عمل دسترسی ندارید', status=403)
        elif self.request.user.type == 's':
            subject = get_object_or_404(Subject, pk=self.kwargs['pk'])
            if subject.course not in self.request.user.course_set.all():
                return Response('شما به این عمل دسترسی ندارید', status=403)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class SavedPostsListCreate(generics.ListCreateAPIView):
    serializer_class = SavePostSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LargeResultsSetPagination

    def post(self, request, *args, **kwargs):
        if self.request.user.type == 't':
            post = get_object_or_404(Post, pk=self.kwargs['pk'], subject__course__teacher=self.request.user)
            post.savedby.add(self.request.user)
            return Response('ذخیره شد', status=201)
        elif self.request.user.type == 's':
            post = get_object_or_404(Post, pk=self.kwargs['pk'], subject__course__coursestudent__in=[
                get_object_or_404(CourseStudent, user=self.request.user,
                                  course=get_object_or_404(Post, pk=self.kwargs['pk']).subject.course)])
            post.savedby.add(self.request.user)
            return Response('ذخیره شد', status=201)
        else:
            return Response('شما به این عمل دسترسی ندارید', status=403)

    def get_queryset(self):
        return self.request.user.post_set.all()


class RemoveSavedPosts(generics.ListCreateAPIView):
    serializer_class = SavePostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if self.request.user.type == 't':
            post = get_object_or_404(Post, pk=self.kwargs['pk'], subject__course__teacher=self.request.user)
            try:
                post.savedby.get(id=self.request.user.id)
                post.savedby.remove(self.request.user)
                return Response('از حالت ذخیره خارج شد', status=201)
            except:
                return Response('شما این پست را ذحیره نکرده اید', status=400)
        elif self.request.user.type == 's':
            post = get_object_or_404(Post, pk=self.kwargs['pk'], subject__course__coursestudent__in=[
                get_object_or_404(CourseStudent, user=self.request.user,
                                  course=get_object_or_404(Post, pk=self.kwargs['pk']).subject.course)])
            if post.savedby.filter(id=self.request.user.id).exists():
                post.savedby.remove(self.request.user)
                return Response('از حالت ذخیره خارج شد', status=201)
            else:
                return Response('شما این پست را ذخیره نکرده اید', status=403)
        else:
            return Response('شما به این عمل دسترسی ندارید', status=403)

    def get_queryset(self):
        return self.request.user.post_set.all()


class LikeCreate(generics.CreateAPIView):
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        serializer.save(post=post, user=self.request.user)

    def post(self, request, *args, **kwargs):
        if self.request.user.type == 't':
            post = get_object_or_404(Post, pk=self.kwargs['pk'], subject__course__teacher=self.request.user)
            if PostLike.objects.filter(post=post, user=self.request.user).exists():
                return Response('شما قبلا این پست را لایک کرده اید.', status=400)
        elif self.request.user.type == 's':
            post_auth = get_object_or_404(Post, pk=self.kwargs['pk'], subject__course__coursestudent__in=[
                get_object_or_404(CourseStudent, user=self.request.user,
                                  course=get_object_or_404(Post, pk=self.kwargs['pk']).subject.course)])
            if PostLike.objects.filter(post=Post.objects.get(pk=self.kwargs['pk']), user=self.request.user).exists():
                return Response('شما قبلا این پست را لایک کرده اید.', status=400)

        else:
            return Response('شما به این عمل دسترسی ندارید', status=403)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class LikeList(generics.ListAPIView):
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        if self.request.user.type == 's':
            return PostLike.objects.filter(
                post=get_object_or_404(Post, pk=self.kwargs['pk'], subject__course__coursestudent__in=[
                    get_object_or_404(CourseStudent, user=self.request.user,
                                      course=get_object_or_404(Post, pk=self.kwargs['pk']).subject.course)]))
        elif self.request.user.type == 't':
            return PostLike.objects.filter(
                post=get_object_or_404(Post, pk=self.kwargs['pk'], subject__course__teacher=self.request.user))


class LikeDestroy(generics.DestroyAPIView):
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = PostLike.objects.all()

    def delete(self, request, *args, **kwargs):
        get_object_or_404(PostLike, user=self.request.user, post=get_object_or_404(Post, pk=self.kwargs['pk'])).delete()
        return Response('Deleted', status=200)


class CommentCreate(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.type == 't':
            post = get_object_or_404(Post, pk=self.kwargs['pk'], subject__course__teacher=self.request.user)
            serializer.save(post=post, user=self.request.user)
        elif self.request.user.type == 's':
            post_auth = get_object_or_404(Post, pk=self.kwargs['pk'], subject__course__coursestudent__in=[
                    get_object_or_404(CourseStudent, user=self.request.user,
                                      course=get_object_or_404(Post, pk=self.kwargs['pk']).subject.course)])
            serializer.save(post=get_object_or_404(Post, pk=self.kwargs['pk']), user=self.request.user)
        else:
            return Response('شما به این عمل دسترسی ندارید', status=403)


class CommentList(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CommentSetPagination

    def get_queryset(self):
        return PostComment.objects.filter(post=get_object_or_404(Post, pk=self.kwargs['pk']))


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
                return Response('شما به این عمل دسترسی ندارید', status=403)

        elif self.request.user.type == 's':
            comment = PostComment.objects.get(pk=self.kwargs['pk'], user=self.request.user)
            if comment:
                return self.destroy(self, request, *args, **kwargs)
            else:
                return Response('شما به این عمل دسترسی ندارید', status=403)

        else:
            return Response('شما به این عمل دسترسی ندارید', status=403)


class ExerciseList(generics.ListAPIView):
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LargeResultsSetPagination

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
    pagination_class = LargeResultsSetPagination

    def perform_authentication(self, request):
        if self.request.user.type != 't':
            raise ValidationError('شما به این عمل دسترسی ندارید')

    def get_queryset(self):
        exercise = Exercise.objects.get(pk=self.kwargs['pk'], teacher=self.request.user)
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
        if self.request.user in [e.user for e in exerciseCourseStudent]:
            serializer.save(exercise=exercise, user=self.request.user)
        else:
            raise ValidationError('شما به این عمل دسترسی ندارید')


class AnswerRD(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticated]
    queryset = Answer.objects.all()

    def perform_authentication(self, request):
        if self.request.user.type != 's':
            raise ValidationError('فقط دانشجویان می توانند جواب تمرین را تغییر دهند!')

    def get(self, request, *args, **kwargs):
        answer = Answer.objects.get(pk=self.kwargs['pk'])
        if answer.user == self.request.user:
            return self.retrieve(request, *args, **kwargs)
        else:
            raise ValidationError('شما به این عمل دسترسی ندارید')

    def put(self, request, *args, **kwargs):
        answer = Answer.objects.get(pk=self.kwargs['pk'])
        if answer.user == self.request.user:
            return self.update(request, *args, **kwargs)
        else:
            raise ValidationError('شما به این عمل دسترسی ندارید')

    def patch(self, request, *args, **kwargs):
        answer = Answer.objects.get(pk=self.kwargs['pk'])
        if answer.user == self.request.user:
            return self.partial_update(request, *args, **kwargs)
        else:
            raise ValidationError('شما به این عمل دسترسی ندارید')

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
    pagination_class = LargeResultsSetPagination

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
    pagination_class = LargeResultsSetPagination

    def perform_authentication(self, request):
        if self.request.user.type != 't':
            raise ValidationError('فقط اساتید میتوانند تمارین خود را ببینند')

    def get_queryset(self):
        return Exercise.objects.filter(teacher=self.request.user)


class CourseSearchList(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get']
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        if self.request.user.type == 't':
            return Course.objects.filter(title__startswith=self.kwargs['course'], teacher=self.request.user)
        elif self.request.user.type == 's':
            return Course.objects.filter(title__startswith=self.kwargs['course'], student__in=[self.request.user])


class SubjectSearchList(generics.ListAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get']
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        if self.request.user.type == 't':
            return Subject.objects.filter(title__startswith=self.kwargs['subject'], course__teacher=self.request.user)
        if self.request.user.type == 's':
            return Subject.objects.filter(title__startswith=self.kwargs['subject'],
                                          course__student__in=[self.request.user])


class CourseStudentSearchList(generics.ListAPIView):
    serializer_class = CourseStudentSerializer
    permission_classes = [permissions.IsAuthenticated, p.IsTeacher]
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        return CourseStudent.objects.filter(course=self.kwargs['pk'], course__teacher=self.request.user,
                                            user__name__startswith=self.kwargs['studentName'])


class NotAnswerStudentList(generics.ListAPIView):
    serializer_class = UserAnswerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        a = []
        b = []
        for i in Answer.objects.filter(exercise=Exercise.objects.get(pk=self.kwargs['pk'])):
            a.append(i.user.id)
        for j in CourseStudent.objects.filter(course=Exercise.objects.get(pk=self.kwargs['pk']).course):
            if j.user.id not in a:
                b.append(j.user.id)
        return CourseStudent.objects.filter(user__id__in=b,
                                            course=Exercise.objects.get(pk=self.kwargs['pk']).course).distinct()


class AnswerStudentList(generics.ListAPIView):
    serializer_class = UserAnswerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        a = []
        for i in Answer.objects.filter(exercise=Exercise.objects.get(pk=self.kwargs['pk'])):
            a.append(i.user.id)
        return CourseStudent.objects.filter(user__id__in=a,
                                            course=Exercise.objects.get(pk=self.kwargs['pk']).course).distinct()


class ExercisePut(generics.UpdateAPIView):
    serializer_class = ExerciseSerializer
    permission_classes = [IsAuthenticated]
    queryset = Exercise.objects.all()


class StudentAnswerCheck(generics.ListAPIView):
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Answer.objects.filter(exercise=Exercise.objects.get(pk=self.kwargs['pk']), user=self.request.user)


class CourseStudentDelete(generics.DestroyAPIView):
    serializer_class = CourseStudentSerializer
    permission_classes = [permissions.IsAuthenticated, p.IsTeacher]
    queryset = CourseStudent.objects.all()

    def delete(self, request, *args, **kwargs):
        student = get_object_or_404(CourseStudent, pk=kwargs['pk'], course=kwargs['coursepk'],
                                    course__teacher=self.request.user)
        student.delete()
        return self.destroy(self, request, *args, **kwargs)