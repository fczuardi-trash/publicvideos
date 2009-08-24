from django.db import models

class Video(models.Model):
  """A video clip instance. The metadata about the clip and it's
  original uploaded file.
  """
  STATUS_CHOICES = (
    ('pending_upload_to_s3', 'Upload pending'),
    ('pending_transcoding', 'Uploaded, transcoding pending'),
    ('transcoding', 'Transcoding'),
    ('transcoded', 'Transcoded'),
  )
  title = models.CharField(max_length=100, blank=True, null=True)
  description = models.CharField(max_length=500, blank=True, null=True)
  mimetype = models.CharField(max_length=40, blank=True, null=True)
  extension = models.CharField(max_length=10, blank=True, null=True)
  s3_key = models.CharField(max_length=40, blank=True, null=True)
  status = models.CharField(choices=STATUS_CHOICES, max_length=sorted(len(status) \
    for status,description in STATUS_CHOICES)[-1])
  created_at = models.DateTimeField('datetime created_at', null=True)
  updated_at = models.DateTimeField('datetime updated_at', null=True)
  width = models.PositiveIntegerField(blank=True, null=True)
  height = models.PositiveIntegerField(blank=True, null=True)
  size = models.PositiveIntegerField(blank=True, null=True, help_text='File size in bytes.')
  duration = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True, help_text='Clip duration in seconds.')
  filename = models.CharField(max_length=100, blank=True, null=True, help_text='The filename of the original file.')
  mute_export = models.NullBooleanField(blank=True)
  # thumbnail, author, credit, copyright, keywords, category ?
  def __unicode__(self):
    return self.title

class TranscodingJob(models.Model):
  """The object representing a video transcoding process, the conversion
  of a video file of one format into another.
  Example: 60fps 1920x1080 mts to 30fps 640x360 ogg.
  """
  description = models.CharField(max_length=100, blank=True, null=True)
  job_slug = models.CharField(max_length=15, blank=True, null=True)

class TranscodingPass(models.Model):
  """The object representing an individual step (encoding pass) in a 
  transcoding job, usually this means one call to a video converter tool.
  Different TranscodingJobs may share some TranscodingPass steps, for 
  example: the convertion from an original camera file to an 
  intermediate format can be the first step of different TranscodingJobs
  """
  from_extension = models.CharField(max_length=10, blank=True, null=True)
  to_extension = models.CharField(max_length=10, blank=True, null=True)
  description = models.CharField(max_length=100, blank=True, null=True)
  command = models.TextField()

class TranscodingJobPass(models.Model):
  """The relationship table for transcoding steps and transcoding jobs.
  """
  transcoding_job = models.ForeignKey(TranscodingJob, blank=True, null=True)
  transcoding_pass = models.ForeignKey(TranscodingPass, blank=True, null=True)
  use_result_from = models.ForeignKey('self', blank=True, null=True)
  step_number = models.PositiveIntegerField(blank=True, null=True)

class VideoVersion(models.Model):
  """A video derivate, the files that are actually used by the website.
  """
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
