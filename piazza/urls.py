from django.contrib import admin
from django.urls import path, include
from . import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from master import views as ms

urlpatterns = [
    path('soren/', include('master.urls')),
    path('soren-auth', include('rest_framework.urls')),
    path('signup/', ms.Signup.as_view(), name='signup'),
    path('signin/', ms.Signin.as_view(), name='signin'),
    path('forgotpassword/', ms.ForgotPassword.as_view(), name='forgot_password'),
    path('forgotpassword/verification/', ms.Verification.as_view(), name='verification'),
    path('forgotpassword/verification/changepassword/', ms.FPChangePassword.as_view(), name='FPChangePassword'),
    path('profile/', ms.Profile.as_view(), name='profile'),
    path('changepassword/', ms.ChangePassword.as_view(), name='change_password'),
    path('support/', ms.Support.as_view(), name='support'),

    path('admin/', admin.site.urls),
    # documentations
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

APP_NAME = 'سورن'
admin.site.site_header = 'پنل مدیریت ' + APP_NAME
admin.site.site_title = APP_NAME
admin.site.index_title = 'صفحه مدیریت'
