from django.db import models

class Video(models.Model):
  description = models.CharField(max_length=100, blank=True, null=True)
  mimetype = models.CharField(max_length=40, blank=True, null=True)
  s3_key = models.CharField(max_length=40, blank=True, null=True)
  created_at = models.DateTimeField('datetime created_at', null=True)
  updated_at = models.DateTimeField('datetime updated_at', null=True)