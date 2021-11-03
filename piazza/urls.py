from django.contrib import admin
from django.urls import path, include
from . import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from master import views as ms

urlpatterns = [
    path('soren/', include('master.urls')),
    path('soren-auth', include('rest_framework.urls')),
    path('signup/', ms.Signup.as_view(), name='Signup'),
    path('signup/verification/', ms.SVerification.as_view(), name='SVerification'),
    path('signin/', ms.Signin.as_view(), name='Signin'),
    path('forgotpassword/', ms.ForgotPassword.as_view(), name='Forgot_Password'),
    path('forgotpassword/verification/', ms.Verification.as_view(), name='Verification'),
    path('forgotpassword/verification/changepassword/', ms.FPChangePassword.as_view(), name='FP_Change_Password'),
    path('profile/', ms.Profile.as_view(), name='Profile'),
    path('deleteaccount/', ms.DeleteAccount.as_view(), name='Delete_Account'),
    path('changeemail/', ms.ChangeEmail.as_view(), name='Change_Email'),
    path('changeemail/emailverification', ms.EmailVerification.as_view(), name='EmailVerification'),
    path('changepassword/', ms.ChangePassword.as_view(), name='Change_Password'),
    path('support/', ms.Support.as_view(), name='Support'),

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
