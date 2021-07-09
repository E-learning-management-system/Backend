from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions
from .serializers import *


@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            message = 'Login Successful!'
        else:
            message = 'Login Failed!'
        return HttpResponse(message)
    else:
        return HttpResponse('GET Method')


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
