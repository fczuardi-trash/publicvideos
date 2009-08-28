from __future__ import with_statement
import sys
import os

base = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(base, os.path.pardir, 'apps'))
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
EC2_ENVIRONMENT = False

class S3UploaderDaemon(daemon.Daemon):
  BASEDIR = base # part of hack inside lib/daemon.py
  log_filename = os.path.join(base, '..', 'log', 's3_uploader.log')
  logging.basicConfig(filename=log_filename, level=logging.INFO)
  TMP_VIDEO_ROOT ='%s/tmp/publicvideos/uploaded' % ('/mnt' if EC2_ENVIRONMENT else '')
  S3_BUCKET_NAME = 'camera'
  def get_tmp_video(self, md5):
    with open(os.path.join(S3UploaderDaemon.TMP_VIDEO_ROOT, md5), 'rb') as f:
      return f.read()
  def main(self):
    while True:
      try:
        cursor = models.conn.cursor()
        utils.lock_on_string(cursor, 'video_queue', 1000000);
        try:
          current_video = models.Video.objects.filter(status='pending_upload_to_s3')[0]
        except:
          utils.unlock_on_string(cursor, 'video_queue')
          time.sleep(10)
          continue
        remote_check = S3_CONN._make_request('HEAD', 'camera', 'originals/%s' % current_video.md5, {}, {})
        if remote_check.status == 200:
          logging.info("File %s already exists on S3." % current_video.md5)
        else:
          tmp_video_file = self.get_tmp_video(current_video.md5)
          logging.info("Got pending video %s and started uploading to S3." % current_video.md5)
          options = {'Content-Type': current_video.mimetype or 'application/octet-stream', 'X-Amz-Acl': 'private'}
          S3_CONN.put(S3UploaderDaemon.S3_BUCKET_NAME, "originals/%s" % current_video.md5, S3.S3Object(tmp_video_file), options)
          logging.info("Finished uploading %s to S3." % current_video.md5)
        current_video.status = 'pending_transcoding'
        current_video.save()
        utils.unlock_on_string(cursor, 'video_queue');
      except:
        file_name = os.path.join(base, '..', 'log', 's3_uploader-%s.error' % str(time.time()).replace('.', ''))
        logging.info("OMGWTFLOLBBQ: %s." % file_name)
        error_details = open(file_name, 'w')
        traceback.print_exc(file=error_details)
        error_details.close()
        time.sleep(15)

if __name__ == '__main__':
  AWS_CREDENTIALS = utils.load_aws_credentials(base)
  S3_CONN = S3.AWSAuthConnection(AWS_CREDENTIALS.S3.access_key, AWS_CREDENTIALS.S3.secret_key)
  S3UploaderDaemon().main()