from django.urls import path
from master import views as ms

urlpatterns = [
    path('courses/', ms.CourseList.as_view()),
    path('newcourse/', ms.CourseCreate.as_view()),
    path('courseRUD/<int:pk>', ms.CourseRUD.as_view()),
    path('courses/<int:pk>/subjects', ms.SubjectList.as_view()),
    path('exercises/', ms.ExerciseListCreate.as_view()),
    path('exercises/<int:pk>', ms.ExerciseRUD.as_view()),
    path('exercises/<int:pk>/answers', ms.ExerciseAnswerListCreate.as_view())
]
