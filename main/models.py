from django.db import models

class Video(models.Model):
  description = models.CharField(max_length=100)
  s3_key = models.CharField(max_length=40)
  created_at = models.DateTimeField('datetime created_at')
  updated_at = models.DateTimeField('datetime updated_at')