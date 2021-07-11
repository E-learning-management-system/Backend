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

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        data = {'نام کاربری : ': user.username, '\nکلمه عبور : ': user.password}
        send_mail('بازیابی کلمه عبور',
                  data,
                  'no-reply-khu@markop.ir',
                  [user.email])


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
        return CourseStudent.objects.filter(course=self.kwargs['pk'])


class CourseStudentCreate(generics.CreateAPIView):
    serializer_class = CourseStudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_authentication(self, request):
        if self.request.user.type != 't':
            raise ValidationError('Access Denied')

    def perform_create(self, serializer):
        pass


class SubjectCreate(generics.CreateAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_authentication(self, request):
        if self.request.user.type != 't':
            raise ValidationError('شما به این عمل دسترسی ندارید')

    def perform_create(self, serializer):
        serializer.save(course=Course.objects.get(pk=self.kwargs['pk']))


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
        subject = Subject.objects.filter(pk=kwargs['pk'])
        if subject.exists():
            return self.destroy(request, *args, **kwargs)

    def perform_update(self, serializer):
        if self.request.user.type != 't':
            raise ValidationError('شما به این عمل دسترسی ندارید')


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
