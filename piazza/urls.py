from django.contrib import admin
from django.urls import path, include
from master import views as ms

urlpatterns = [
    path('api/', include('master.urls')),
    path('api-auth', include('rest_framework.urls')),
    path('signup/', ms.Signup.as_view(), name='signup'),
    path('signin/', ms.Signin.as_view(), name='signin')

    # path('admin/', admin.site.urls),
    # path('changepassword/', ms.user_change_password, name='user_change_password'),
]

APP_NAME = 'Piazza'
admin.site.site_header = 'پنل مدیریت' + APP_NAME
admin.site.site_title = APP_NAME
admin.site.index_title = 'صفحه مدیریت'
