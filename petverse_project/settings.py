"""
Django settings for petverse_project.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep secret key safe
SECRET_KEY = 'django-insecure-y5g37@67%hiwvz+z$yyk5k0)439p^+k!x7!-ivvr*x#)&ac+j5'

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# -------------------------------------------------------------
# Applications
# -------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # PetVerse Apps
    'core',
    'accounts',
    'pets',
    'adoptions',
    'services',
]


# -------------------------------------------------------------
# Middleware
# -------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'petverse_project.urls'


# -------------------------------------------------------------
# Templates
# -------------------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        # Very Important:
        # Your HTML template folder is inside core/templates
        'DIRS': [BASE_DIR / 'core' / 'templates'],

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

WSGI_APPLICATION = 'petverse_project.wsgi.application'


# -------------------------------------------------------------
# Database (SQLite for development)
# -------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

"""
# -------------------------------------------------------------
# MySQL Database (Uncomment when needed)
# -------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'petverse_db',
        'USER': 'root',
        'PASSWORD': 'your_mysql_password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}
"""


# -------------------------------------------------------------
# Authentication
# -------------------------------------------------------------
AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


# -------------------------------------------------------------
# Password Validation
# -------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# -------------------------------------------------------------
# Internationalization
# -------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True


# -------------------------------------------------------------
# Static & Media Files
# -------------------------------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'core' / 'static',   # your existing template static folder
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# -------------------------------------------------------------
# Default primary key
# -------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# -------------------------------------------------------------
# Project roles (used by forms/views)
# -------------------------------------------------------------
PETVERSE_ROLES = [
    ('adopter', 'Adopter'),
    ('owner', 'Pet Owner'),
    ('shelter', 'Shelter'),
    ('admin', 'Admin'),
]
