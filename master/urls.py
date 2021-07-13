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
    path('post-rud/<int:pk>', ms.PostRUD.as_view()),
    path('posts/<int:pk>/newlike', ms.LikeCreate.as_view()),
    path('posts/<int:pk>/likes', ms.LikeList.as_view()),
    path('removelike/<int:pk>/', ms.LikeDestroy.as_view()),
    path('posts/<int:pk>/newcomment', ms.CommentCreate.as_view()),
    path('posts/<int:pk>/comments', ms.CommentList.as_view()),
    path('deletecomment/<int:pk>', ms.CommentDelete.as_view()),

    #################################################################
    path('exercise', ms.ExerciseListCreate.as_view()),
    path('exercise/<int:pk>', ms.ExerciseRUD.as_view()),
    path('exercise/<int:pk>/answer', ms.ExerciseAnswerListCreate),
    path('exercise/<int:pk>/tag', ms.TagListCreate.as_view()),
    path('answer/<int:pk>', ms.ExerciseAnswerRUD.as_view()),
    path('tag/<int:pk>', ms.TagRUD.as_view()),
]
