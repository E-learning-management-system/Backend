from django.urls import path
from master import views as ms

urlpatterns = [
    path('courses/', ms.CourseListCreate.as_view()),
    path('courses/<int:pk>', ms.CourseRUD.as_view()),
    path('courses/<int:pk>/subjects', ms.SubjectListCreate.as_view()),
]
