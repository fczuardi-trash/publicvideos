from django.db import models

class Video(models.Model):
  STATUS_CHOICES = (
    ('pending_upload_to_s3', 'Upload pending'),
    ('pending_transcoding', 'Uploaded, transcoding pending'),
    ('transcoding', 'Transcoding'),
    ('transcoded', 'Transcoded'),
  )
  title = models.CharField(max_length=100, blank=True, null=True)
  description = models.CharField(max_length=500, blank=True, null=True)
  mimetype = models.CharField(max_length=40, blank=True, null=True)
  s3_key = models.CharField(max_length=40, blank=True, null=True)
  status = models.CharField(choices=STATUS_CHOICES, max_length=sorted(len(status) \
    for status,description in STATUS_CHOICES)[-1])
  created_at = models.DateTimeField('datetime created_at', null=True)
  updated_at = models.DateTimeField('datetime updated_at', null=True)
  width = models.PositiveIntegerField(blank=True, null=True)
  height = models.PositiveIntegerField(blank=True, null=True)
  size = models.PositiveIntegerField(blank=True, null=True, help_text='File size in bytes.')
  duration = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True, help_text='Clip duration in seconds.')
  mute_export = models.NullBooleanField(blank=True)
  # thumbnail, author, credit, copyright, keywords, category ?
  def __unicode__(self):
    return self.title

class TranscodingJob(models.Model):
  description = models.CharField(max_length=100, blank=True, null=True)
  job_slug = models.CharField(max_length=15, blank=True, null=True)

class TranscodingPass(models.Model):
  description = models.CharField(max_length=100, blank=True, null=True)
  command = models.TextField()

class TranscodingJobPass(models.Model):
  transcoding_job = models.ForeignKey(TranscodingJob, blank=True, null=True)
  transcoding_pass = models.ForeignKey(TranscodingPass, blank=True, null=True)
  step_number = models.PositiveIntegerField(blank=True, null=True)

class VideoVersion(models.Model):
  source = models.ForeignKey(Video, blank=True, null=True)
  url = models.URLField(verify_exists=False, max_length=400, blank=True, null=True)
  mimetype = models.CharField(max_length=40, blank=True, null=True)
  width = models.PositiveIntegerField(blank=True, null=True)
  height = models.PositiveIntegerField(blank=True, null=True)
  size = models.PositiveIntegerField(blank=True, null=True, help_text='File size in bytes.')
  duration = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True, help_text='Clip duration in seconds.')
  transcoded_with = models.ForeignKey(TranscodingJob, blank=True, null=True)
  codecs = models.CharField(max_length=40, blank=True, null=True, help_text='HTML5 \
    <a href="http://www.whatwg.org/specs/web-apps/current-work/#attr-source-type">codecs</a> string.')
  # bitrate, framerate, samplingrate, channels, lang, player ?
  def __unicode__(self):
    return self.url
