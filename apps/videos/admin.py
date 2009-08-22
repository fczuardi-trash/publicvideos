from videos.models import Video, TranscodingJob, TranscodingPass, TranscodingJobPass, VideoVersion
from django.contrib import admin

class VideoAdmin(admin.ModelAdmin):
  fieldsets = [
    (None, {'fields': ['description', 's3_key', 'mimetype', 'created_at']})
  ]

admin.site.register(Video, VideoAdmin)
admin.site.register(TranscodingJob)
admin.site.register(TranscodingPass)
admin.site.register(TranscodingJobPass)
admin.site.register(VideoVersion)