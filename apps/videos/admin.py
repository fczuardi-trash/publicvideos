from videos.models import Video, TranscodingJob, TranscodingPass, TranscodingJobPass, VideoVersion
from django.contrib import admin

class VideoAdmin(admin.ModelAdmin):
  list_display = ('filename', 'md5', 'status', 'set_slug')

admin.site.register(Video, VideoAdmin)
admin.site.register(TranscodingJob)
admin.site.register(TranscodingPass)
admin.site.register(TranscodingJobPass)
admin.site.register(VideoVersion)
