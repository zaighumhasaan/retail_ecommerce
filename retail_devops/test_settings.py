"""
Test settings for Retail DevOps application.
Separate settings for testing to ensure clean test environment.
"""

from .settings import *
import os

# Override settings for testing
DEBUG = False
TEMPLATE_DEBUG = False

# Use in-memory SQLite for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Disable password hashing for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging during tests
LOGGING_CONFIG = None

# Use faster session backend
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Disable cache for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Disable email sending during tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Test-specific settings
ALLOWED_HOSTS = ['testserver', '127.0.0.1', 'localhost']

# Disable CSRF for API tests
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False

# Media files for testing
MEDIA_ROOT = os.path.join(BASE_DIR, 'test_media')
MEDIA_URL = '/test_media/'

# Static files for testing
STATIC_ROOT = os.path.join(BASE_DIR, 'test_static')

# Disable admin interface customization for tests
# This ensures tests run with default admin interface
ADMIN_INTERFACE_CUSTOMIZATION = False

# Test-specific middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Test-specific installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

# Disable debug toolbar and other development tools
INTERNAL_IPS = []

# Test-specific secret key
SECRET_KEY = 'test-secret-key-for-testing-only'

# Disable internationalization for tests
USE_I18N = False
USE_L10N = False
USE_TZ = False

# Test-specific timezone
TIME_ZONE = 'UTC'

# Disable file upload handling for tests
FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
]

# Test-specific file upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440  # 2.5 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440  # 2.5 MB

# Disable password validation for faster tests
AUTH_PASSWORD_VALIDATORS = []

# Test-specific session settings
SESSION_COOKIE_AGE = 86400  # 1 day
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Test-specific CSRF settings
CSRF_COOKIE_AGE = 31449600  # 1 year
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'

# Test-specific security settings
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
X_FRAME_OPTIONS = 'DENY'

# Disable admin interface customization for tests
ADMIN_INTERFACE_CUSTOMIZATION = False
