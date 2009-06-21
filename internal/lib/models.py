from __future__ import with_statement
from django.conf import settings
from utils import jshash

with jshash() as conf:
  conf.DATABASE_ENGINE = 'mysql'
  conf.DATABASE_HOST = 'localhost'
  conf.DATABASE_NAME = 'publicvideos_dev'
  conf.DATABASE_USER = 'm1ch43l'
  conf.DATABASE_PASSWORD = 'p4l1n'
  conf.INSTALLED_APPS = ('s3_uploader',)
  settings.configure(**conf)

from django.db import models
from django.db import connection as conn

class Video(models.Model):
  description = models.CharField(max_length=100, blank=True, null=True)
  mimetype = models.CharField(max_length=40, blank=True, null=True)
  s3_key = models.CharField(max_length=40, blank=True, null=True)
  status = models.CharField(max_length=sorted(len(status) for status in \
    'pending_upload_to_s3 pending_transcoding transcoding transcoded'.split())[-1])
  created_at = models.DateTimeField('datetime created_at', null=True)
  updated_at = models.DateTimeField('datetime updated_at', null=True)
  class Meta:
    app_label = 's3_uploader'
    db_table = 'main_video'