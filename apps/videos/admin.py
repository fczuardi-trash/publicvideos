from videos.models import Video, TranscodingJob, TranscodingPass, TranscodingJobPass, VideoVersion
from django.contrib import admin
import urllib2
import time
import datetime

class VideoVersionAdmin(admin.ModelAdmin):
  list_display = ('source', 'url')
  date_hierarchy = 'created_at'
  list_filter = ['created_at']
  search_fields = ['url']

class TranscodingJobAdmin(admin.ModelAdmin):
  list_display = ('job_slug', 'description')
  
class VideoAdmin(admin.ModelAdmin):
  save_on_top = True
  list_display = ('filename', 'md5', 'status', 'author', 'set_slug', 'fps_choice', 'created_at')
  list_filter = ['status', 'set_slug']
  list_editable = ['status']
  search_fields = ['filename', '^md5', 'set_slug']
  date_hierarchy = 'created_at'
  actions = [
    'update_status_to_transcoded',
    'update_status_to_transcoding',
    'update_status_to_pending_transcoding',
    'update_fps_choice_to_30',
    'check_archive_and_create_video_versions',
  ]
  
  def update_fps_choice(self, request, queryset, new_fps):
    rows_updated = queryset.update(fps_choice=new_fps)
    if rows_updated == 1:
      message_bit = "1 video was"
    else:
      message_bit = "%s video were" % rows_updated
    self.message_user(request, "%s successfully marked as %s." % (message_bit, new_fps))
    
  def update_status(self, request, queryset, new_status):
    rows_updated = queryset.update(status=new_status)
    if rows_updated == 1:
      message_bit = "1 video was"
    else:
      message_bit = "%s video were" % rows_updated
    self.message_user(request, "%s successfully marked as %s." % (message_bit, new_status))
  def update_status_to_transcoded(self, request, queryset):
    self.update_status(request, queryset, 'transcoded')
  def update_status_to_pending_transcoding(self, request, queryset):
    self.update_status(request, queryset, 'pending_transcoding')
  def update_status_to_transcoding(self, request, queryset):
    self.update_status(request, queryset, 'transcoding')
  def update_fps_choice_to_30(self, request, queryset):
    self.update_fps_choice(request, queryset, 30)
    
  def check_archive_and_create_video_versions(self, request, queryset):
    """Manually generate the video versions for videos that were uploaded already
    to archive.org but aren't on publicvideo's database.
    
    This will lookup archive.org for the expected version URLs for the selected
    Video objects and if they exist, create or update the correspondent 
    VideoVersion objects.
    """
    video_versions_count = 0
    jobs = TranscodingJob.objects.all()
    for video in queryset:
      for job in jobs:
        to_extension = job.job_slug[4:7].upper()
        job_slug_parts = job.job_slug.split('-')
        framerate = job_slug_parts[1][-2:]
        if (framerate == '24' or framerate == '30'):
          if (int(video.fps_choice) != int(framerate)):
            continue
        if to_extension == 'DIR':
          to_extension = 'OGV'
        if to_extension == 'WEB':
          to_extension = 'WEBM'
        archive_url = "http://www.archive.org/download/%s/%s.%s.%s" % (video.set_slug, video.md5, job.job_slug, to_extension)
        try:
          video_version = VideoVersion.objects.get(url=archive_url)
        except:
          video_version = VideoVersion()
        try:
          response = urllib2.urlopen(archive_url)
          info = response.info()
          video_version.source = video
          video_version.url = archive_url
          video_version.mimetype = info['Content-Type']
          video_version.size = info['Content-Length']
          video_version.width = job.width
          video_version.height = job.height
          # Archive.org headers use las-modified with this format: Wed, 09 Sep 2009 07:57:25 GMT
          video_version.updated_at = datetime.datetime.fromtimestamp(
            time.mktime(
              time.strptime(info['Last-Modified'], "%a, %d %b %Y %H:%M:%S %Z")
            )
          )
          video_version.transcoded_with = job
          if (video_version.created_at is None):
            video_version.created_at = video_version.updated_at
          video_version.save()
          video_versions_count += 1
        except urllib2.HTTPError, e:
          self.message_user(request, "Error fetching %s <br/>%s" % (archive_url, e.code))
    self.message_user(request, "%s VideoVersions created/updated." % video_versions_count)

admin.site.register(Video, VideoAdmin)
admin.site.register(VideoVersion, VideoVersionAdmin)
admin.site.register(TranscodingJob, TranscodingJobAdmin)
admin.site.register(TranscodingPass)
admin.site.register(TranscodingJobPass)
