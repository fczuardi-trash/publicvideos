from __future__ import with_statement
import os
import sha
import time
import mimetypes
import base64
import hmac, sha
import logging
import traceback
import pprint

from django.conf import settings
from django.utils import simplejson

from django import forms
from django.forms.widgets import Input
from django.contrib.auth.forms import UserCreationForm

from django.http import HttpResponse, HttpResponseRedirect
from lib.jinjasupport import render_to_response

from videos.models import Video


def index(request):
  videos = Video.objects.all()
  return render_to_response("videos/index.html", {})
  
def simple_upload_videos(request):
  # generate S3 policy and signature
  policy_document = {
    'expiration': '2020-08-14T22:17:09Z', # '%sZ' % datetime.datetime.utcnow().isoformat()[:-7]
    'conditions': [
      {'bucket': 'camera'},
      ['starts-with', '$key', 'originals/'],
      {'acl': 'private'},
      #{'success_action_redirect': 'http://localhost:8000/clips/simple_upload'},
      ['content-length-range', 0, 104857600]
    ] 
  }
  policy = base64.b64encode(simplejson.dumps(policy_document, ensure_ascii=False))
  signature = base64.b64encode(hmac.new(settings.AWS_CREDENTIALS.S3.secret_key, policy, sha).digest())
  bucket = 'camera'
  access_key = settings.AWS_CREDENTIALS.S3.access_key
  acl = 'private'
  redirect_url = 'http://localhost:8000/clips/simple)upload'
  content_type = 'application/octet-stream'
  return render_to_response("videos/html_upload.html", locals())

def upload_videos(request):
  try:
    uploaded_files = None
    if request.method == 'POST':
      for k in request.FILES.keys():
        uploaded_file = request.FILES[k]
        uploaded_file_content = uploaded_file.read()
        name, ext = os.path.splitext(uploaded_file.name)
        uploaded_video = Video()
        uploaded_video.filename = uploaded_file.name
        uploaded_video.size = uploaded_file.size
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
