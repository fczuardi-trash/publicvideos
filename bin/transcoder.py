from __future__ import with_statement
import sys
import os

base = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(base, os.path.pardir, os.path.pardir, os.path.pardir, 'apps'))
sys.path.append(os.path.join(base, os.path.pardir))
sys.path.append(os.path.join(base, os.path.pardir, 'lib'))

import lockfile
import daemon
import logging
import commands
import ConfigParser
import time
import traceback
import datetime
import S3
import utils
import models
EC2_ENVIRONMENT = False

class TranscoderDaemon(old_daemon.Daemon):
  BASEDIR = base # part of hack inside lib/daemon.py
  default_conf = os.path.join(base, '..', 'config', 'transcoder.conf')
  section = 'transcoder' # which should conventionally be the same as the filename
  TMP_VIDEO_ROOT = '%s/tmp/publicvideos/transcoding_limbo' % ('/mnt' if EC2_ENVIRONMENT else '')
  if not os.path.exists(os.path.join(TMP_VIDEO_ROOT, 'originals')):
    os.makedirs(os.path.join(TMP_VIDEO_ROOT, 'originals'))
  S3_BUCKET_NAME = 'camera'
  def save_tmp_video_and_create_references(self, current_video):
    original_filename = "%s.%s.%s" % (current_video.s3_key, '0',  'mts')
    original_path = os.path.join(TranscoderDaemon.TMP_VIDEO_ROOT, 'originals', original_filename)
    logging.info("os.path.exists(original_path): %s, %s" % (str(os.path.exists(original_path)), original_path))
    if not os.path.exists(original_path):
      response = S3_CONN.get(TranscoderDaemon.S3_BUCKET_NAME, "originals/%s" % current_video.s3_key)
      with open(original_path, 'wb') as f:
        logging.info("f = open('%s', 'wb')" % original_path)
        logging.info("writing: %s" % response.object.data[0:10])
        f.write(response.object.data)
    for job in self.jobs:
      try:
        os.symlink(original_path, os.path.join(TranscoderDaemon.TMP_VIDEO_ROOT, job.job_slug, original_filename))
      except OSError:
        pass
  def put_the_result_back_in_s3(self, current_video, job_slug, result, result_extension):
    options = {'Content-Type': current_video.mimetype or 'application/octet-stream', 'X-Amz-Acl': 'private'}
    with open(result, 'rb') as f:
      result = f.read()
    transcoded_file = S3.S3Object(result)
    S3_CONN.put(TranscoderDaemon.S3_BUCKET_NAME, "%s/%s.%s" % (job_slug, current_video.s3_key, result_extension), transcoded_file, options)
    return S3_URL_GENERATOR.generate_url('GET', TranscoderDaemon.S3_BUCKET_NAME, "%s/%s" % (job_slug, current_video.s3_key))  
  def load_jobs(self):
    self.jobs = models.TranscodingJob.objects.all()
    for job in self.jobs:
      if not os.path.exists(os.path.join(TranscoderDaemon.TMP_VIDEO_ROOT, job.job_slug)):
        os.makedirs(os.path.join(TranscoderDaemon.TMP_VIDEO_ROOT, job.job_slug))
  def main(self):
    if not os.path.exists(TranscoderDaemon.TMP_VIDEO_ROOT):
      os.makedirs(TranscoderDaemon.TMP_VIDEO_ROOT)
    self.load_jobs()
    while True:
      try:
        cursor = models.conn.cursor()
        utils.lock_on_string(cursor, 'video_queue', 1000000);
        try:
          current_video = models.Video.objects.filter(status='pending_transcoding')[0]
        except IndexError:
          utils.unlock_on_string(cursor, 'video_queue')
          time.sleep(10)
          continue
        logging.info("Downloading original video %s so we can transcode the shit out of it." % current_video.s3_key)
        self.save_tmp_video_and_create_references(current_video)        
        current_video.status = 'transcoding'
        current_video.save()
        utils.unlock_and_lock_again_real_quick(cursor, 'video_queue')
        logging.info("Preparing to run transcoding jobs on video %s." % current_video.s3_key)
        for job in self.jobs:
          job_passes = job.transcodingjobpass_set.select_related().order_by('step_number')
          for job_pass in job_passes:
            logging.info('steps: %s' % range(1, job_pass.step_number)[::-1])
            for step in range(1, job_pass.step_number+1)[::-1]:
              source_pass_filename = '%s.%s.%s' % (current_video.s3_key, str(step-1), job_pass.transcoding_pass.from_extension)
              logging.info('---> %s: ' % source_pass_filename)
              source_pass_path = os.path.join(TranscoderDaemon.TMP_VIDEO_ROOT, job.job_slug, source_pass_filename)
              if os.path.exists(source_pass_path):
                break
            target_extension = job_pass.transcoding_pass.to_extension
            target_pass_filename = '%s.%s.%s' % (current_video.s3_key, str(job_pass.step_number), target_extension)
            target_pass_path = os.path.join(TranscoderDaemon.TMP_VIDEO_ROOT, job.job_slug, target_pass_filename)
            command = job_pass.transcoding_pass.command.replace('$SOURCE', source_pass_path).replace('$TARGET', target_pass_path)
            logging.info("Running: %s" % command)
            command_status, command_output = commands.getstatusoutput(command)
          logging.info("Transcode completed, uploading result back to S3.")
          source_url = self.put_the_result_back_in_s3(current_video, job.job_slug, target_pass_path, target_extension)
          models.VideoVersion(video=current_video, trancoded_with=job, url=source_url)
          logging.info("Transcoded and uploaded video %s with the %s encoding." % (current_video.s3_key, job.job_slug))          
        utils.unlock_on_string(cursor, 'video_queue');
      except:
        current_video.status = 'pending_transcoding'
        current_video.save()
        file_name = os.path.join(base, '..', 'log', 'transcoder-%s.error' % str(time.time()).replace('.', ''))
        logging.info("OMGWTFLOLBBQ: %s." % file_name)
        error_details = open(file_name, 'w')
        traceback.print_exc(file=error_details)
        error_details.close()
        time.sleep(15)

def main():
  AWS_CREDENTIALS = utils.load_aws_credentials(base)
  ac, sk = AWS_CREDENTIALS.S3.access_key, AWS_CREDENTIALS.S3.secret_key
  S3_CONN = S3.AWSAuthConnection(ac, sk)
  S3_URL_GENERATOR = S3.QueryStringAuthGenerator(ac, sk, is_secure=False)
  S3_URL_GENERATOR.set_expires_in(60*60*2)
  # from wonderful PEP 3143: http://www.python.org/dev/peps/pep-3143/
  daemon_context = daemon.DaemonContext()
  daemon_context.pidfile = lockfile.FileLock(join(base, 'pids', 'transcoder.pid'))
  with daemon_context:
    transcoder = TranscoderDaemon()
    transcoder.main()

if __name__ == '__main__':
  try: main()
  except: traceback.print_exc(file=sys.stdout)