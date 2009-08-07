from __future__ import with_statement
import sys
import os

base = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(base, os.path.pardir))
sys.path.append(os.path.join(base, os.path.pardir, 'lib'))

import daemon
import logging
import ConfigParser
import time
import traceback
import datetime
import S3
import utils
import models

class TranscoderDaemon(daemon.Daemon):
  BASEDIR = base # part of hack inside lib/daemon.py
  default_conf = os.path.join(base, '..', 'config', 'transcoder.conf')
  section = 'transcoder' # which should conventionally be the same as the filename
  TMP_VIDEO_ROOT = '/mnt/tmp/publicvideos/transcoding_limbo'
  S3_BUCKET_NAME = 'camera'
  def get_transcoded_video(self, job_slug, s3_key):
    with open(os.path.join(TranscoderDaemon.TMP_VIDEO_ROOT, job_slug, s3_key), 'rb') as f:
      return f.read()
  def save_tmp_video(self, s3_key):
    data = S3_CONN.get(TranscoderDaemon.S3_BUCKET_NAME, "originals/%s" % s3_key)
    with open(os.path.join(S3UploaderDaemon.TMP_VIDEO_ROOT, s3_key), 'wb') as f:
      f.write(data)
  def put_the_result_back_in_s3(self, job_slug, current_video):
    options = {'Content-Type': current_video.mimetype or 'application/octet-stream', 'X-Amz-Acl': 'private'}
    transcoded_file = S3.S3Object(self.get_transcoded_video(job_slug, current_video.s3_key))
    S3_CONN.put(TranscoderDaemon.S3_BUCKET_NAME, "%s/%s" % (job_slug, current_video.s3_key), transcoded_file, options)
  def run(self):
    while True:
      try:
        cursor = models.conn.cursor()
        utils.lock_on_string(cursor, 'video_queue', 1000000);
        try:
          current_video = models.Video.objects.filter(status='pending_transcoding')[0]
        except:
          utils.unlock_on_string(cursor, 'video_queue')
          time.sleep(30)
          continue
        logging.info("Downloading original video %s so we can transcode the shit out of it." % current_video.s3_key)
        self.save_tmp_video(current_video.s3_key)
        jobs = models.TranscodingJob.objects.all()
        current_video.status = 'transcoding'
        current_video.save
        utils.unlock_and_lock_again_real_quick(cursor, 'video_queue')
        for job in jobs:
          # todo: transcoding magic here, figure out how to dynamically replace source and target filepaths
          self.put_the_result_back_in_s3(current_video, job.job_slug)
          VideoVersion(video=current_video, trancoded_with=job, source='') # todo: generate signed source link
          logging.info("Transcoded and uploaded video %s with the %s encoding." % (current_video.s3_key, job.job_slug))          
        utils.unlock_on_string(cursor, 'video_queue');
      except:
        file_name = os.path.join(base, '..', 'log', 'transcoder-%s.error' % str(time.time()).replace('.', ''))
        logging.info("!!!!!!!!! OMGWTFLOL !!!1111oneeleven")
        logging.info("!!!!!!!!! CANT HAZ CHEEZEBURGER. Logged the error here: %s." % file_name)
        error_details = open(file_name, 'w')
        traceback.print_exc(file=error_details)
        error_details.close()
        time.sleep(15)


if __name__ == '__main__':
  AWS_CREDENTIALS = utils.load_aws_credentials()
  S3_CONN = S3.AWSAuthConnection(AWS_CREDENTIALS.S3.access_key, AWS_CREDENTIALS.S3.secret_key)
  TranscoderDaemon().main()