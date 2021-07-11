from django.urls import path
from master import views as ms

urlpatterns = [
    path('courses/', ms.CourseList.as_view()),
    path('newcourse/', ms.CourseCreate.as_view()),
    path('course-rud/<int:pk>/', ms.CourseRUD.as_view()),
    path('courses/<int:pk>/students/', ms.CourseStudentList.as_view()),
    path('courses/<int:pk>/newstudent/', ms.CourseStudentCreate.as_view()),
    path('student-rd/<int:pk>/', ms.CourseStudentRD.as_view()),
    path('courses/<int:pk>/subjects/', ms.SubjectList.as_view()),
    path('courses/<int:pk>/newsubject/', ms.SubjectCreate.as_view()),
    path('subject-rud/<int:pk>/', ms.SubjectRUD.as_view()),
    path('courses/<int:pk>/newpost/', ms.PostCreate.as_view()),
    path('courses/<int:pk>/posts/', ms.PostList.as_view()),
    path('post-rud/', ms.PostRUD.as_view()),

    #################################################################
    path('exercises/', ms.ExerciseList.as_view()),
    path('newexercise/', ms.ExerciseCreate.as_view()),

    path('exercises-rud/<int:pk>', ms.ExerciseRUD.as_view()),
    path('exercises/<int:pk>/answers', ms.ExerciseAnswerList.as_view()),
    path('exercises/<int:pk>/newanswer', ms.ExerciseAnswerCreate.as_view()),
    path('exerciseanswer-rud/<int:pk>', ms.ExerciseAnswerRUD.as_view()),
    path('exercises/<int:pk>/tags', ms.TagList.as_view()),
    path('exercises/<int:pk>/newtag', ms.TagCreate.as_view()),
]
