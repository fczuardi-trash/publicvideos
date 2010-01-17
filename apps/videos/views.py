# -*- coding: utf-8 -*-

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
import random


from django.conf import settings
from django.utils import simplejson

from django import forms
from django.forms.widgets import Input
from django.contrib.auth.forms import UserCreationForm

from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from lib.jinjasupport import render_to_response

from videos.models import Video
from videos.models import VideoVersion
from django.contrib.auth.models import User

def index(request, set_slug=None, fmt='html'):
  didyoumean = None
  query_text = 'Search'
  page_title = 'Public Videos(alpha)'
  canonical_url = 'http://alpha.publicvideos.org/'
  template_path = "videos/index.html"
  if 'set' in request.GET:
    set_slug = request.GET['set']
  if 'fmt' in request.GET:
    fmt = request.GET['fmt']
  try:
    if set_slug:
      videos = Video.objects.filter(status='transcoded').filter(set_slug__exact=set_slug).order_by('filename')
      author_name = u"%s %s" % (videos[0].author.first_name, videos[0].author.last_name) if videos[0].author.first_name else str(videos[0].author)
      results_num = len(videos)
      is_search_results = True
      page_title = u'Clip Set “%s” by %s — Public Videos(alpha)' % (set_slug,author_name)
      canonical_url = 'http://alpha.publicvideos.org/set/%s/' % set_slug
      if fmt == 'sitemap':
        template_path = 'videos/set_sitemap.xml'
    elif 'q' in request.GET:
      if request.GET['q'].strip() != '':
        is_search_results = True
        query_text = request.GET['q']
        results_num = 103
        videos = Video.objects.filter(status='transcoded').filter(filename__contains=query_text).order_by('?')
        page_title = u'Free Stock Video Footage: %s — Public Videos(alpha)' % query_text.capitalize()
        canonical_url = 'http://alpha.publicvideos.org/?q=%s' % query_text
        if(len(videos) == 0):
          import keyword_list
          page_title = u'no results for “%s” — Public Videos(alpha)' % query_text
          didyoumeans = keyword_list.get_whitelist()
          didyoumean = random.choice(didyoumeans)
    else:
      if fmt == 'sitemap':
        return render_to_response('videos/other_urls_sitemap.xml')
      videos = Video.objects.filter(status='transcoded').order_by('?')
      results_num = 64
      is_search_results = False
  except IndexError:
    raise Http404
  # http://www.archive.org/download/ace_200907_01/33470ecf16669eb165619a9e229ce751.mts-jpg-108.JPG.JPG
  # http://static.publicvideos.org/thumbnails/ace_200910_03/1f3e8ef1f7967b7d39d2ca8158f865d2.mts-jpgbw-108.JPG
  thumbs = []
  for video in videos[:results_num]:
    # url = "http://www.archive.org/download/%s/%s.%s" % (video.set_slug, video.md5, 'mts-jpg-108.JPG')
    url = "http://static.publicvideos.org/thumbnails/%s/%s.%s" % (video.set_slug, video.md5, 'mts-jpg-108.JPG')
    page = "/%s" % video.md5[:7]
    simplified_filename = video.filename[video.filename.rfind('_')+1:-4]
    tags = simplified_filename.split('-')
    alt = tags[0]
    video = video
    thumbs.append({'src':url,'page':page, 'alt':alt, 'tags':tags, 'video':video })
  return render_to_response(template_path, {
    'page_title': page_title,
    'canonical_url': canonical_url,
    'query_text':query_text,
    'thumbs':thumbs,
    'is_search_results':is_search_results,
    'didyoumean':didyoumean
    })

def sitemap_index(request):
  return list_sets(request, fmt='sitemap')

def list_sets(request, fmt='html'):
  page_title = u"Free Clips Directory, browse by clip sets. — Public Videos(alpha)"
  canonical_url = 'http://alpha.publicvideos.org/sets/'
  template_path = "videos/sets.html"
  if 'fmt' in request.GET:
    fmt = request.GET['fmt']
  if fmt == 'sitemap':
    template_path = "videos/sitemap_index.xml"
  available_sets = [
    {'contributor':'Ace', 'year':'2009', 'month':'May', 'part':'1 of 6', 'set_slug':'ace_200905_01'},
    {'contributor':'Ace', 'year':'2009', 'month':'May', 'part':'2 of 6', 'set_slug':'ace_200905_02'},
    {'contributor':'Ace', 'year':'2009', 'month':'May', 'part':'3 of 6', 'set_slug':'ace_200905_03'},
    {'contributor':'Ace', 'year':'2009', 'month':'May', 'part':'4 of 6', 'set_slug':'ace_200905_04'},
    {'contributor':'Ace', 'year':'2009', 'month':'June', 'part':'1 of 6', 'set_slug':'ace_200907_01'},
    {'contributor':'Ace', 'year':'2009', 'month':'June', 'part':'2 of 6', 'set_slug':'ace_200907_02'},
    {'contributor':'Ace', 'year':'2009', 'month':'June', 'part':'3 of 6', 'set_slug':'ace_200907_03'},
    {'contributor':'Ace', 'year':'2009', 'month':'June', 'part':'4 of 6', 'set_slug':'ace_200907_04'},
    {'contributor':'Ace', 'year':'2009', 'month':'June', 'part':'5 of 6', 'set_slug':'ace_200907_05'},
    {'contributor':'Ace', 'year':'2009', 'month':'June', 'part':'6 of 6', 'set_slug':'ace_200907_06'},
    {'contributor':'Ace', 'year':'2009', 'month':'October', 'part':'1 of 3', 'set_slug':'ace_200910_01'},
    {'contributor':'Ace', 'year':'2009', 'month':'October', 'part':'2 of 3', 'set_slug':'ace_200910_02'},
    {'contributor':'Ace', 'year':'2009', 'month':'October', 'part':'3 of 3', 'set_slug':'ace_200910_03'},
    {'contributor':'Ace', 'year':'2009', 'month':'November', 'part':'1 of 6', 'set_slug':'ace_200911_01'},
    {'contributor':'Ace', 'year':'2009', 'month':'November', 'part':'2 of 6', 'set_slug':'ace_200911_02'},
    {'contributor':'Ace', 'year':'2009', 'month':'November', 'part':'3 of 6', 'set_slug':'ace_200911_03'},
    {'contributor':'Ace', 'year':'2009', 'month':'November', 'part':'4 of 6', 'set_slug':'ace_200911_04'},
    {'contributor':'Ace', 'year':'2009', 'month':'November', 'part':'5 of 6', 'set_slug':'ace_200911_05'},
    {'contributor':'Ace', 'year':'2009', 'month':'November', 'part':'6 of 6', 'set_slug':'ace_200911_06'},
    {'contributor':'Ace', 'year':'2009', 'month':'December', 'part':'1 of 4', 'set_slug':'ace_200912_01'},
    {'contributor':'Ace', 'year':'2009', 'month':'December', 'part':'2 of 4', 'set_slug':'ace_200912_02'},
    {'contributor':'Ace', 'year':'2009', 'month':'December', 'part':'3 of 4', 'set_slug':'ace_200912_03'},
    {'contributor':'Ace', 'year':'2009', 'month':'December', 'part':'4 of 4', 'set_slug':'ace_200912_04'}
  ]
  return render_to_response(template_path, locals())
  
def show(request, short=None, rubish=None, id=None):
  try:
    if id:
      video = Video.objects.get(pk=id)
    elif 'id' in request.GET:
      video = Video.objects.get(pk=request.GET['id'])
    elif short:
      video = Video.objects.filter(status='transcoded').filter(md5__startswith=short).order_by('created_at')[0]
    else:
      video = Video.objects.filter(status='transcoded').order_by('?')[0]
  except IndexError:
    raise Http404
  video_versions = VideoVersion.objects.filter(source=video)
  versions = {}
  for version in video_versions:
    urlparts = version.url.split('-')
    version_name = urlparts[-1]
    if urlparts[-2] == 'jpgbw': version_name = "%s.BW" % version_name
    versions[str(version_name)] = version
  video_title = video.title if video.title else "Clip #%s" % video.pk
  author_name = u"%s %s" % (video.author.first_name, video.author.last_name) if video.author.first_name else str(video.author)
  host_link = "http://www.archive.org/details/%s" % video.set_slug
  page_title = u"“%s” — Public Videos(alpha)" % video_title
  canonical_url = 'http://alpha.publicvideos.org/clip/%s/' % video.pk
  keywords = video.filename[video.filename.rfind('_')+1:-4]
  keywords = keywords.replace('-',', ')
  unsuported_video_tag_msg = u"""
  <p class="middle">
  The following <b>clip</b> works better in browsers with<br>
          <b>native html5 video support</b><br>
  We recommend the download of <a href="http://www.mozilla.com/en-US/firefox/all-beta.html"><b>firefox 3.6 beta</b></a>
  </p>
  <div class="bottom">
  <p class="useflash">
  (but you can still <a href="#" class="play-button">watch it using flash</a> or 
  download it using the link below)
  </p>
  <p class="left bottomlink"><a href="http://www.playogg.org">www.playogg.org</a></p>
  <p class="right bottomlink"><a href="http://www.mozilla.org">www.mozilla.org</a></p>
  </div>"""
  return render_to_response("videos/show.html", dict(locals()))
  
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
        if not os.path.exists(os.path.join(settings.TMP_VIDEO_ROOT, 'originals', set_slug)):
          os.makedirs(os.path.join(settings.TMP_VIDEO_ROOT, 'originals', set_slug))
        original_filename = "%s.%s" % (uploaded_video.md5, uploaded_video.extension)
        with open(os.path.join(settings.TMP_VIDEO_ROOT, 'originals', set_slug, original_filename), 'wb') as f:
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