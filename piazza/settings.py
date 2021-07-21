from pathlib import Path
import locale
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-j$y3y78*fsu4%!xn!n=@yq7y)qt7g8ar*9nez0s=py&cy(-*cp'

DEBUG = True

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", '').split(
    " ") if os.environ.get("DJANGO_ALLOWED_HOSTS", '') else []

INSTALLED_APPS = [
    'master',
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    
    # https://drf-spectacular.readthedocs.io/en/latest/readme.html
    'drf_spectacular',

    # django-filter, see: https://django-filter.readthedocs.io/en/latest/guide/rest_framework.html
    'django_filters',
]
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',

    ],
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer',
                                 'rest_framework.renderers.BrowsableAPIRenderer'],

    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 1000,
}
SPECTACULAR_SETTINGS = {
    'TITLE': 'Your Project API',
    'DESCRIPTION': 'Your project description',
    'VERSION': '1.0.0',
    # OTHER SETTINGS
}
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'piazza.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'piazza.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('SQL_ENGINE', 'django.db.backends.mysql'),
        'NAME': os.environ.get('SQL_DATABASE', 'piazza_db'),
        'USER': os.environ.get('SQL_USER', 'piazza'),
        'PASSWORD': os.environ.get('SQL_PASSWORD', 'piazza_1234'),
        'HOST': os.environ.get('SQL_HOST', 'localhost'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'fa-ir'

locale.setlocale(locale.LC_ALL, "fa_IR.UTF-8")

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATIC_ROOT = BASE_DIR / 'static'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'master.User'

# Files and Images size
# 2 MB
MAX_UPLOAD_FILE_SIZE = '2097152'
# 1 MB
MAX_UPLOAD_IMAGE_SIZE = '1048576'

EMAIL_HOST = 'mail.markop.ir'
EMAIL_HOST_USER = 'no-reply-khu@markop.ir'
EMAIL_HOST_PASSWORD = 'fuw9MUM7rir!lunk'
EMAIL_PORT = '587'
EMAIL_USE_TLS = True
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
