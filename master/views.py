from django.http import HttpResponse
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import generics, permissions, status
from rest_framework.parsers import JSONParser

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
        user = User.objects.get(email=serializer.validated_data['email'],
                                type=serializer.validated_data['type'],
                                university=serializer.validated_data['university'])
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


@csrf_exempt
def user_change_password(request):
    if request.method == 'POST':
        try:
            new_password = request.POST['new_password']
            u = request.user
            u.set_password(new_password)
            u.save()
            return HttpResponse('Password Changed Successfully!')
        except:
            return HttpResponse('Password Changed Process Failed!')
    else:
        return HttpResponse('GET Method')


class CourseListCreate(generics.ListCreateAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        if self.request.user.type != 't':
            raise ValidationError('شما به این عمل دسترسی ندارید')
        else:
            if self.request.method == 'POST':
                data = JSONParser().parse(self.request)
                startdate = data['start_date']
                enddate = data['end_date']
                examdate = data['exam_date']
                if startdate > enddate:
                    raise ValidationError('تاریخ شروع درس باید پیش از تاریخ پایان آن باشد')
                elif examdate < startdate:
                    raise ValidationError('تاریخ امتحان باید بعد از تاریخ شروع کلاس ها باشد')
                else:
                    serializer.save(teacher=self.request.user)

    def get_queryset(self):
        if self.request.user.type == 't':
            return Course.objects.filter(teacher=self.request.user)
        else:
            return CourseStudent.objects.all()


class CourseRUD(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Course.objects.filter(teacher=self.request.user)

    def delete(self, request, *args, **kwargs):
        course = Course.objects.get(pk=kwargs['pk'], teacher=self.request.user)
        if course.exists():
            return self.destroy(request, *args, **kwargs)
        else:
            raise ValidationError('شما به این عمل دسترسی ندارید')


class SubjectListCreate(generics.ListCreateAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Subject.objects.filter(course_id=self.kwargs['pk'])

    def perform_create(self, serializer):
        if self.request.user.type != 't':
            raise ValidationError('شما به این عمل دسترسی ندارید')
        else:
            serializer.save(course_id=self.kwargs['pk'], course=Course.objects.get(pk=self.kwargs['pk']))


class ExerciseListCreate(generics.ListCreateAPIView):
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Exercise.objects.filter(author=self.request.user)

    def perform_create(self, serializer):
        if self.request.user.type == 't':
            serializer.save(author=self.request.user)
        else:
            raise ValidationError('فقظ اساتید قابلیت ایجاد به این عمل دسترسی دارند')


class ExerciseRUD(generics.RetrieveDestroyAPIView):
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.type == 't':
            return Exercise.objects.filter(author=self.request.user)


class ExerciseAnswerListCreate(generics.ListCreateAPIView):
    serializer_class = ExAnswerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        exercise = Exercise.objects.get(pk=self.kwargs['pk'])
        if user.type == 's':
            if exercise.deadline > datetime.now():
                serializer.save(author=self.request.user, exercise=Exercise.objects.get(pk=self.kwargs['pk']))
            else:
                raise ValidationError('مهلت پاسخ دهی به اتمام رسیده است')

    def get_queryset(self):
        if self.request.user.type == 't':
            return ExerciseAnswer.objects.filter(exercise=Exercise.objects.get(pk=self.kwargs['pk']))
