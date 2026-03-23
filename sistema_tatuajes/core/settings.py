"""
Django settings for core project.
"""

from pathlib import Path
import os
from decouple import config, Csv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ─── Seguridad ────────────────────────────────────────────────────────────────

SECRET_KEY = config('SECRET_KEY', default='change-this-secret-key-in-production')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1,.pythonanywhere.com,.railway.app,mojberlin.pythonanywhere.com',
    cast=Csv(),
)

CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='https://*.pythonanywhere.com,https://*.railway.app,https://mojberlin.pythonanywhere.com',
    cast=Csv(),
)


# ─── Aplicaciones ─────────────────────────────────────────────────────────────

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Nuestras Apps
    'usuarios',
    'citas',
    'cotizaciones',
    'portafolio',
    'health',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',        # sirve estáticos en producción
    'django.contrib.sessions.middleware.SessionMiddleware',
    'usuarios.middleware.TenantMiddleware',              # resuelve request.studio por subdominio
    'django.middleware.locale.LocaleMiddleware',         # i18n: detecta idioma del visitante
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'usuarios.context_processors.notificaciones',
                'usuarios.context_processors.estudio',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# ─── Base de datos ────────────────────────────────────────────────────────────
# En producción, define DATABASE_URL=postgres://user:pass@host:5432/dbname
# En desarrollo local, usa SQLite como fallback.

DATABASE_URL = config('DATABASE_URL', default=None)

if DATABASE_URL:
    import dj_database_url          # noqa: E402
    DATABASES = {'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ─── Validación de contraseñas ────────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ─── Internacionalización ─────────────────────────────────────────────────────

from django.utils.translation import gettext_lazy as _

LANGUAGES = [
    ('es', _('Spanish')),
    ('en', _('English')),
]

LANGUAGE_CODE = 'es'

LOCALE_PATHS = [BASE_DIR / 'locale']

TIME_ZONE = 'America/Mexico_City'

USE_I18N = True
USE_L10N = True
USE_TZ = True


# ─── Archivos estáticos ───────────────────────────────────────────────────────

STATIC_URL = '/static/'
# Solo incluir static/ si existe (en producción puede no estar commiteada).
STATICFILES_DIRS = [d for d in [BASE_DIR / 'static'] if d.exists()]
STATIC_ROOT = BASE_DIR / 'staticfiles'         # destino de collectstatic

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ─── Archivos de media (subidos por usuarios) ─────────────────────────────────
# En producción, considera usar un bucket S3 / DigitalOcean Spaces.

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ─── Correo electrónico ───────────────────────────────────────────────────────

EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend',
)
EMAIL_HOST          = config('EMAIL_HOST',     default='smtp.gmail.com')
EMAIL_PORT          = config('EMAIL_PORT',     default=587,  cast=int)
EMAIL_USE_TLS       = config('EMAIL_USE_TLS',  default=True, cast=bool)
EMAIL_HOST_USER     = config('EMAIL_HOST_USER',    default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL  = config('DEFAULT_FROM_EMAIL', default='estudio@tatuajes.com')


# ─── Autenticación ────────────────────────────────────────────────────────────

LOGIN_URL          = '/cuentas/login/'
LOGIN_REDIRECT_URL = '/panel/post-login/'
LOGOUT_REDIRECT_URL = '/portafolio/'


# ─── Seguridad en producción ──────────────────────────────────────────────────

if not DEBUG:
    SECURE_PROXY_SSL_HEADER     = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST        = True
    SECURE_SSL_REDIRECT         = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
    SESSION_COOKIE_SECURE       = True
    CSRF_COOKIE_SECURE          = True
    SECURE_BROWSER_XSS_FILTER  = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS         = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD         = True
    X_FRAME_OPTIONS             = 'DENY'


# ─── Misc ─────────────────────────────────────────────────────────────────────

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


if SECRET_KEY == 'change-this-secret-key-in-production' and not DEBUG:
    print('WARNING: SECRET_KEY no está configurada en entorno de producción.')
