import os
import sys
import logging
import ConfigParser

class jshash(dict):
  def __getattr__(self, k):
    if self.has_key(k): return self[k]
    raise AttributeError, repr(k)
  def __setattr__(self, k, v): self[k] = v
  def __delattr__(self, k): del self[k]
  def __enter__(self): return self
  def __exit__(self, type, value, tv): pass

def load_aws_credentials(config_path):
  AWS_CREDENTIALS = jshash({'S3':jshash()})
  config_file = os.path.join(config_path, 'aws.conf')
  parsed_config = ConfigParser.ConfigParser()
  parsed_config.read(config_file)
  for section in parsed_config.sections():
    service = section.split(':')[1]
    if service == 's3':
      AWS_CREDENTIALS.S3.access_key = parsed_config.get(section, 'access_key')
      AWS_CREDENTIALS.S3.secret_key = parsed_config.get(section, 'secret_key')
  return AWS_CREDENTIALS

CONFIG_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config')
AWS_CREDENTIALS = load_aws_credentials(CONFIG_PATH)

# add the apps subdirectory in the path
base = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(base, 'apps'))

logging.basicConfig(
  level = logging.DEBUG,
  format = '%(asctime)s %(levelname)s %(message)s',
)

# Django settings for publicvideos project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
  ('Jonas Galvez', 'jonasgalvez@gmail.com'),
  ('Fabricio Zuardi', 'fabricio@fabricio.org')
)

#if working on Amazon EC2 AMIs set to True
EC2_ENVIRONMENT = False

#text file to append error details
DEBUG_ERROR_FILE = os.path.join(os.path.dirname(__file__), 'log/error.txt').replace('\\','/')

MANAGERS = ADMINS

# create database publicvideos_dev default character set utf8;
# grant all on publicvideos_dev.* to m1ch43l@localhost identified by 'p4l1n'; 

DATABASE_ENGINE = 'mysql' # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'publicvideos_dev' # Or path to database file if using sqlite3.
DATABASE_USER = 'm1ch43l' # Not used with sqlite3.
DATABASE_PASSWORD = 'p4l1n' # Not used with sqlite3.
DATABASE_HOST = '' # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = '' # Set to empty string for default. Not used with sqlite3.
DATABASE_OPTIONS = {
  'init_command': 'SET NAMES "utf8"' # make sure mysql doesn't make poo poo with utf-8
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Sao_Paulo'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

DEFAULT_CONTENT_TYPE = 'text/html'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'static').replace('\\','/')

TMP_VIDEO_ROOT =  ('/mnt' if EC2_ENVIRONMENT else '') + '/tmp/publicvideos/uploaded'

FILE_UPLOAD_TEMP_DIR = TMP_VIDEO_ROOT

DEFAULT_UPLOADED_VIDEO_STATUS = 'pending_upload_to_s3'

if not os.path.exists(TMP_VIDEO_ROOT):
  os.makedirs(TMP_VIDEO_ROOT)
  
FILE_UPLOAD_MAX_MEMORY_SIZE = 80 * (1024*1024) 

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '6@4__^29fd+7lf$vl@x&9*8v7@_%hc()oz(rvlsomjptp8!7$p'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
  'django.template.loaders.filesystem.load_template_source',
  'django.template.loaders.app_directories.load_template_source',
# 'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
  'django_authopenid.context_processors.authopenid',
  'django.core.context_processors.auth',
)


MIDDLEWARE_CLASSES = (
  'django.middleware.common.CommonMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django_authopenid.middleware.OpenIDMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
  os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/'),
)

LOGIN_URL = '/account/login/'
LOGOUT_URL = '/account/logout/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

INSTALLED_APPS = (
  # django contrib apps
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.sites',
  'django.contrib.admin',
  
  # django-authopenid
  'django_authopenid',
  
  #publicvideos stuff
  'users',
  'videos',
)
