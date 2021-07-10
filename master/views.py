from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions
from rest_framework.parsers import JSONParser
from django.db import IntegrityError

from rest_framework.authtoken.models import Token
from .serializers import *


@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
            user = User.objects.create_user(data['username'], password=data['password'])
            user.save()
            token = Token.objects.create(user=user)
            return JsonResponse({'token': str(token)}, status=201)
        except IntegrityError:
            return JsonResponse({'error': 'That username has already been taken. Please choose a new username'},
                                status=400)


@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        user = authenticate(request, username=data['username'], password=data['password'])
        if user is None:
            return JsonResponse({'error': "'Couldn't find the user"},
                                status=400)
        else:
            try:
                token = Token.objects.get(user=user)
            except:
                token = Token.objects.create(user=user)
            return JsonResponse({'token': str(token)}, status=200)


@csrf_exempt
def user_logout(request):
    logout(request)
    return HttpResponse('Logout Successful!')


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
