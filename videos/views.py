from __future__ import with_statement
import os
import sha
import time
import mimetypes
import logging
import traceback
import pprint

from django.conf import settings

from django import forms
from django.forms.widgets import Input
from django.contrib.auth.forms import UserCreationForm

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from videos.models import Video


def index(request):
  videos = Video.objects.all()
  return render_to_response("videos/index.html", {})

def upload_videos(request):
  try:
    uploaded_files = None
    if request.method == 'POST':
      for k in request.FILES.keys():
        uploaded_file = request.FILES[k]
        uploaded_file_content = uploaded_file.read()
        name, ext = os.path.splitext(uploaded_file.name)
        uploaded_video = Video()
        uploaded_video.status = 'pending_upload_to_s3'
        uploaded_video.mimetype = mimetypes.types_map.get(ext)
        uploaded_video.s3_key = sha.new('%s-%s' % (settings.SECRET_KEY, uploaded_file_content)).hexdigest()
        with open(os.path.join(settings.TMP_VIDEO_ROOT, uploaded_video.s3_key), 'wb') as f:
          f.write(uploaded_file_content)
        del uploaded_file_content
        uploaded_video.save()
      return HttpResponse('')
    return render_to_response("videos/upload.html", locals())
  except:
    error_details = open(settings.DEBUG_ERROR_FILE, 'w')
    traceback.print_exc(file=error_details)
    error_details.close()
    #stack = pprint.pformat(traceback.extract_stack())
    #logging.debug('An error occurred: %s' % stack)
