from __future__ import with_statement
import os
import sha
import time
import mimetypes
import hashlib
import base64
import hmac, sha
import traceback
import pprint
import datetime


from django.conf import settings
from django.utils import simplejson

from django import forms
from django.forms.widgets import Input
from django.contrib.auth.forms import UserCreationForm

from django.http import HttpResponse, HttpResponseRedirect
from lib.jinjasupport import render_to_response

from videos.models import Video
from django.contrib.auth.models import User


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
      author_email = request.POST['author']
      set_slug = request.POST['set_slug']
      author = User.objects.filter(email=author_email)[0]
      for k in request.FILES.keys():
        uploaded_file = request.FILES[k]
        uploaded_file_content = uploaded_file.read()
        name, ext = os.path.splitext(uploaded_file.name)
        md5digest = hashlib.md5(uploaded_file_content).hexdigest()
        #if duplicate, overwrite the old
        try:
          uploaded_video = Video.objects.filter(md5=md5digest)[0]
          #TODO make other checkt to see if it is from the same user and the same filename
          # if not raise an error (duplicate md5 from 2 different sources)
        except IndexError:
          uploaded_video = Video()
        uploaded_video.filename = uploaded_file.name
        uploaded_video.size = uploaded_file.size
        uploaded_video.status = settings.DEFAULT_UPLOADED_VIDEO_STATUS
        uploaded_video.extension = ext[1:]
        uploaded_video.mimetype = mimetypes.types_map.get(ext)
        uploaded_video.md5 = md5digest
        delta = datetime.timedelta(days=-46)
        uploaded_video.created_at = datetime.datetime.now()+delta
        uploaded_video.updated_at = datetime.datetime.now()+delta
        uploaded_video.author = author
        uploaded_video.set_slug = set_slug
        if not os.path.exists(os.path.join(settings.TMP_VIDEO_ROOT, 'originals')):
          os.makedirs(os.path.join(settings.TMP_VIDEO_ROOT, 'originals'))
        original_filename = "%s.%s" % (uploaded_video.md5, uploaded_video.extension)
        with open(os.path.join(settings.TMP_VIDEO_ROOT, 'originals', original_filename), 'wb') as f:
          f.write(uploaded_file_content)
        del uploaded_file_content
        uploaded_video.save()
      return HttpResponse('')
    else:
      author_email = request.GET['author'] if 'author' in request.GET else ''
      set_slug = request.GET['set_slug'] if 'set_slug' in request.GET else ''
    return render_to_response("videos/upload.html", locals())
  except:
    error_details = open(settings.DEBUG_ERROR_FILE, 'w')
    traceback.print_exc(file=error_details)
    error_details.close()
    #stack = pprint.pformat(traceback.extract_stack())