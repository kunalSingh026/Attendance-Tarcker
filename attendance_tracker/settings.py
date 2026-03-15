import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv() 

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- 1. SECURITY AND DEBUGGING ---

# SECURITY WARNING: keep the secret key used in production secret!
# Use an environment variable for production (Render) or local .env file
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-hu9%g#5egdh7anr)4!to^s!n@kxvhh!o&kb@2#%+f$8gbf=k!1')

# Detect if running on Render using the RENDER_EXTERNAL_HOSTNAME variable
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')

if RENDER_EXTERNAL_HOSTNAME:
    # Production settings
    DEBUG = False
    ALLOWED_HOSTS = [RENDER_EXTERNAL_HOSTNAME, '127.0.0.1']
    # Secure HTTP settings
    CSRF_TRUSTED_ORIGINS = [f'https://{RENDER_EXTERNAL_HOSTNAME}']
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
else:
    # Development settings
    DEBUG = True
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
    # Add your development hostnames here if needed


# --- 2. INSTALLED APPS ---

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tracker',
]

# --- 3. MIDDLEWARE ---

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise must be above SessionMiddleware for static file efficiency
    "whitenoise.middleware.WhiteNoiseMiddleware", 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- 4. DATABASE CONFIGURATION (Production Ready) ---

if RENDER_EXTERNAL_HOSTNAME:
    # Use DATABASE_URL environment variable if available (PostgreSQL). Otherwise fallback to SQLite for quick deploy.
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        DATABASES = {
            'default': dj_database_url.config(
                default=database_url,
                conn_max_age=600
            )
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
else:
    # Use SQLite for local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# --- 5. STATIC FILES (WhiteNoise Configuration) ---

# The URL prefix for your static files
STATIC_URL = '/static/'

# The directory where collectstatic will gather all static files for deployment
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Directories where Django should look for static files *in addition* to app directories
# This points to your project-level 'static' folder
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Tell WhiteNoise to use Gzip compression and manifest files for caching
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# --- 6. WSGI, TEMPLATES, and other settings ---

ROOT_URLCONF = 'attendance_tracker.urls'

WSGI_APPLICATION = 'attendance_tracker.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata' # Keeping your time zone
USE_I18N = True
USE_TZ = True

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'