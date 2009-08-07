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

class S3UploaderDaemon(daemon.Daemon):
  BASEDIR = base # part of hack inside lib/daemon.py
  default_conf = os.path.join(base, '..', 'config', 's3_uploader.conf')
  section = 's3_uploader' # which should conventionally be the same as the filename
  TMP_VIDEO_ROOT = '/mnt/tmp/publicvideos/uploaded'
  S3_BUCKET_NAME = 'camera'
  def get_tmp_video(self, s3_key):
    with open(os.path.join(S3UploaderDaemon.TMP_VIDEO_ROOT, s3_key), 'rb') as f:
      return f.read()
  def run(self):
    while True:
      try:
        cursor = models.conn.cursor()
        utils.lock_on_string(cursor, 'video_queue', 1000000);
        try:
          current_video = models.Video.objects.filter(status='pending_upload_to_s3')[0]
        except:
          utils.unlock_on_string(cursor, 'video_queue')
          time.sleep(30)
          continue
        logging.info("Got pending video %s and started uploading to S3." % current_video.s3_key)
        tmp_video_file = self.get_tmp_video(current_video.s3_key)
        options = {'Content-Type': current_video.mimetype or 'application/octet-stream', 'X-Amz-Acl': 'private'}
        S3_CONN.put(S3UploaderDaemon.S3_BUCKET_NAME, "originals/%s" % current_video.s3_key, S3.S3Object(tmp_video_file), options)
        logging.info("Finished uploading %s to S3." % current_video.s3_key)
        current_video.status = 'pending_transcoding'
        current_video.save()
        utils.unlock_on_string(cursor, 'video_queue');
      except:
        file_name = os.path.join(base, '..', 'log', 's3_uploader-%s.error' % str(time.time()).replace('.', ''))
        logging.info("!!!!!!!!! OMGWTFLOL !!!1111oneeleven")
        logging.info("!!!!!!!!! CANT HAZ CHEEZEBURGER. Logged the error here: %s." % file_name)
        error_details = open(file_name, 'w')
        traceback.print_exc(file=error_details)
        error_details.close()
        time.sleep(15)

def load_aws_credentials():
  global AWS_CREDENTIALS
  AWS_CREDENTIALS = utils.jshash({'S3':utils.jshash()})
  config_file = os.path.join(base, os.path.pardir, 'config', 'aws.conf')
  parsed_config = ConfigParser.ConfigParser()
  parsed_config.read(config_file)
  for section in parsed_config.sections():
    service = section.split(':')[1]
    if service == 's3':
      AWS_CREDENTIALS.S3.access_key = parsed_config.get(section, 'access_key')
      AWS_CREDENTIALS.S3.secret_key = parsed_config.get(section, 'secret_key')

if __name__ == '__main__':
  load_aws_credentials()
  S3_CONN = S3.AWSAuthConnection(AWS_CREDENTIALS.S3.access_key, AWS_CREDENTIALS.S3.secret_key)
  S3UploaderDaemon().main()