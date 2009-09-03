from videos.models import Video, TranscodingJob, TranscodingPass, TranscodingJobPass, VideoVersion
from django.contrib import admin

admin.site.register(Video)
admin.site.register(TranscodingJob)
admin.site.register(TranscodingPass)
admin.site.register(TranscodingJobPass)
admin.site.register(VideoVersion)