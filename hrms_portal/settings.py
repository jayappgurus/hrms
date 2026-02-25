"""
Django settings for hrms_portal project.
"""

import pymysql
pymysql.install_as_MySQLdb()

from pathlib import Path
import os
import sys

# Apply Python 3.14 compatibility fix
if sys.version_info >= (3, 14):
    try:
        from . import django_py314_fix
    except ImportError:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================
# SECURITY SETTINGS
# ==============================

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-key')

DEBUG = True

ALLOWED_HOSTS = [
    "hrmsportal.app.devlaunchpad.com.au",
    "www.hrmsportal.app.devlaunchpad.com.au",
    "pms.hrmsportal.app.devlaunchpad.com.au",
    "54.252.154.126",
    "127.0.0.1",
    "localhost",
    "*",
]

# ==============================
# APPLICATIONS
# ==============================

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'employees',
    'salary',
    "corsheaders",
]

# ==============================
# MIDDLEWARE
# ==============================

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  

]

# ==============================
# URLS / TEMPLATES
# ==============================

ROOT_URLCONF = 'hrms_portal.urls'

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

WSGI_APPLICATION = 'hrms_portal.wsgi.application'

# ==============================
# DATABASE (MySQL)
# ==============================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'hrmsportalappdev_portal_hrms_db'),
        'USER': os.environ.get('DB_USER', 'hrmsportalappdev_hrmsportalappdev'),
        'PASSWORD': os.environ.get('DB_PASSWORD', '4d^H!I?l^0],roF,'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

# ==============================
# PASSWORD VALIDATION
# ==============================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==============================
# INTERNATIONALIZATION
# ==============================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ==============================
# STATIC / MEDIA
# ==============================

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================
# MESSAGES
# ==============================

from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# ==============================
# AUTHENTICATION
# ==============================

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# ==============================
# CSRF / SESSION SETTINGS
# ==============================

CSRF_TRUSTED_ORIGINS = [
    "https://hrmsportal.app.devlaunchpad.com.au",
    "https://www.hrmsportal.app.devlaunchpad.com.au",
    "http://hrmsportal.app.devlaunchpad.com.au",
    "http://www.hrmsportal.app.devlaunchpad.com.au",
    "https://pms.hrmsportal.app.devlaunchpad.com.au",
    "http://54.252.154.126",
    "http://54.252.154.126:8000",
]

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ==============================
# CORS SETTINGS
# ==============================

CORS_ALLOW_ALL_ORIGINS = True

# ==============================
# ADMIN / JAZZMIN
# ==============================

ADMIN_TITLE = "HRMS Portal Administration"
ADMIN_HEADER = "HRMS Portal"
ADMIN_INDEX_TITLE = "Welcome to HRMS Portal Administration"

JAZZMIN_SETTINGS = {
    "site_title": "HRMS Portal",
    "site_header": "HRMS Portal",
    "site_logo": "images/main-logo.svg",
    "site_icon": "images/favicon.svg",
    "search_model": "employees.department",
    "navigation": [
        {"app": "employees", "label": "Employee Management", "icon": "fas fa-users"},
    ],
    "theme": "darkly",
    "list_per_page": 25,
}

# ==============================
# EMAIL SETTINGS (Mailtrap)
# ==============================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'sandbox.smtp.mailtrap.io'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = '13fff2b7547ed9'
EMAIL_HOST_PASSWORD = 'ddf4b21b3b7140'
DEFAULT_FROM_EMAIL = 'HRMS Portal <hrms@example.com>'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
