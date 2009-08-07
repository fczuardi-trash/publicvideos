from __future__ import with_statement

import sys, os
base = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(base, os.path.pardir, os.path.pardir))

import video.models
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

class Video(video.models.Video):
  class Meta:
    app_label = 's3_uploader'
    db_table = 'main_video'

class VideoVersion(video.models.VideoVersion):
  class Meta:
    app_label = 's3_uploader'
    db_table = 'main_video_version'
    
class TranscodingJob(video.models.TranscodingJob):
  class Meta:
    app_label = 's3_uploader'
    db_table = 'main_transcoding_job'

class TranscodingPass(video.models.TranscodingPass):
  class Meta:
    app_label = 's3_uploader'
    db_table = 'main_transcoding_pass'
    
class TranscodingJobPass(video.models.TranscodingJobPass):
  class Meta:
    app_label = 's3_uploader'
    db_table = 'main_transcoding_job_pass'