from __future__ import with_statement

import sys, os
base = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(base, os.path.pardir, os.path.pardir))

import videos.models
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

# fixme: get rid of the 'class Meta' crap someway somehow

class Video(videos.models.Video):
  class Meta:
    app_label = 's3_uploader'
    db_table = 'videos_video'

class VideoVersion(videos.models.VideoVersion):
  class Meta:
    app_label = 's3_uploader'
    db_table = 'videos_video_version'
    
class TranscodingJob(videos.models.TranscodingJob):
  class Meta:
    app_label = 's3_uploader'
    db_table = 'videos_transcoding_job'

class TranscodingPass(videos.models.TranscodingPass):
  class Meta:
    app_label = 's3_uploader'
    db_table = 'videos_transcoding_pass'
    
class TranscodingJobPass(videos.models.TranscodingJobPass):
  class Meta:
    app_label = 's3_uploader'
    db_table = 'videos_transcoding_job_pass'
