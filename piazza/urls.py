from django.contrib import admin
from django.urls import path, include
from master import views as ms

urlpatterns = [
    path('api/', include('master.urls')),
    path('admin/', admin.site.urls),
    path('signup/', ms.signup),

    path('login/', ms.login, name='user_login'),
    path('logout/', ms.user_logout, name='user_logout'),
    path('changepassword/', ms.user_change_password, name='user_change_password'),
    path('api-auth', include('rest_framework.urls')),
]

APP_NAME = 'Piazza'
admin.site.site_header = 'پنل مدیریت' + APP_NAME
admin.site.site_title = APP_NAME
admin.site.index_title = 'صفحه مدیریت'