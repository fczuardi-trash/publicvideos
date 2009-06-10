from publicvideos_site.main.models import Video
from django.contrib import admin

class VideoAdmin(admin.ModelAdmin):
  fieldsets = [
    (None, {'fields': ['description', 's3_key', 'created_at']})
  ]

admin.site.register(Video, VideoAdmin)
