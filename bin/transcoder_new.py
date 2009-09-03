from __future__ import with_statement
import sys
import os

base = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(base, os.path.pardir))
sys.path.append(os.path.join(base, os.path.pardir, 'apps'))
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
import shutil

EC2_ENVIRONMENT = False

class TranscoderDaemon():
  BASEDIR = base # part of hack inside lib/daemon.py
  TMP_VIDEO_ROOT = '%s/tmp/publicvideos/' % ('/mnt' if EC2_ENVIRONMENT else '')
  if not os.path.exists(os.path.join(TMP_VIDEO_ROOT, 'originals')):
    os.makedirs(os.path.join(TMP_VIDEO_ROOT, 'originals'))
  if not os.path.exists(os.path.join(TMP_VIDEO_ROOT, 'transcoding')):
    os.makedirs(os.path.join(TMP_VIDEO_ROOT, 'transcoding'))
  S3_BUCKET_NAME = 'camera'
  def save_tmp_video_and_create_references(self, current_video):
    original_filename = "%s.%s" % (current_video.md5, current_video.extension)
    original_path = os.path.join(TranscoderDaemon.TMP_VIDEO_ROOT, 'originals', original_filename)
    f = open('/Users/fczuardi/trampos/publicvideos/log/transcoder.log', 'a')
    f.write("\nos.path.exists(original_path): %s, %s" % (str(os.path.exists(original_path)), original_path));f.close();
    logging.info("os.path.exists(original_path): %s, %s" % (str(os.path.exists(original_path)), original_path))
    if not os.path.exists(original_path):
      f = open('/Users/fczuardi/trampos/publicvideos/log/transcoder.log', 'a')
      f.write("\nfile does not exist locally, try fetching it from s3");f.close();
      logging.info("file does not exist locally, try fetching it from s3")
      response = S3_CONN.get(TranscoderDaemon.S3_BUCKET_NAME, "originals/%s" % current_video.md5)
      with open(original_path, 'wb') as f:
        logging.info("f = open('%s', 'wb')" % original_path)
        logging.info("writing: %s" % response.object.data[0:10])
        f.write(response.object.data)
  def put_the_result_back_in_video_tmp(self, current_video, job_slug, result, result_extension):
    if not os.path.exists(os.path.join(TranscoderDaemon.TMP_VIDEO_ROOT, 'versions')):
      os.makedirs(os.path.join(TranscoderDaemon.TMP_VIDEO_ROOT, 'versions'))
    version_filename = "%s.%s.%s" % (current_video.md5, job_slug,  result_extension)
    version_path = os.path.join(TranscoderDaemon.TMP_VIDEO_ROOT, 'versions', version_filename)
    shutil.copy2(result, version_path)
    return version_path
  def put_the_result_back_in_s3(self, current_video, job_slug, result, result_extension):
    options = {'Content-Type': current_video.mimetype or 'application/octet-stream', 'X-Amz-Acl': 'private'}
    with open(result, 'rb') as f:
      result = f.read()
    transcoded_file = S3.S3Object(result)
    S3_CONN.put(TranscoderDaemon.S3_BUCKET_NAME, "%s/%s.%s" % (job_slug, current_video.md5, result_extension), transcoded_file, options)
    return S3_URL_GENERATOR.generate_url('GET', TranscoderDaemon.S3_BUCKET_NAME, "%s/%s" % (job_slug, current_video.md5))  
  def debug_log(self, msg):
    file_name = os.path.join(base, '..', 'log', 'transcoder.log')
    f = open(file_name, 'a')
    f.write(msg);
    f.close();
    return
  def main(self):
    self.debug_log("\n testing")
    if not os.path.exists(TranscoderDaemon.TMP_VIDEO_ROOT):
      os.makedirs(TranscoderDaemon.TMP_VIDEO_ROOT)
    # self.load_jobs()
    self.jobs = models.TranscodingJob.objects.all()
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
        self.debug_log("\nDownloading original video %s so we can transcode the shit out of it." % current_video.md5)
        logging.info("Downloading original video %s so we can transcode the shit out of it." % current_video.md5)
        self.save_tmp_video_and_create_references(current_video)        
        current_video.status = 'transcoding'
        current_video.save()
        utils.unlock_and_lock_again_real_quick(cursor, 'video_queue')
        self.debug_log("\nPreparing to run transcoding jobs on video %s." % current_video.md5);
        logging.info("Preparing to run transcoding jobs on video %s." % current_video.md5)
        for job in self.jobs:
          self.debug_log("\n\n Job: %s." % job.job_slug);
          job_passes = job.transcodingjobpass_set.select_related().order_by('step_number')
          current_pass_stack = ''
          original_filename = "%s.%s" % (current_video.md5, current_video.extension)
          original_path = os.path.join(TranscoderDaemon.TMP_VIDEO_ROOT, 'originals', original_filename)
          source_pass_path = original_path
          for job_pass in job_passes:
            self.debug_log("\n\n Job Pass: %s." % job_pass.transcoding_pass);
            current_pass_stack = "%s__%s" % (current_pass_stack, job_pass.transcoding_pass.slug)
            self.debug_log("\ncurrent_pass_stack: %s" % current_pass_stack);
            target_extension = job_pass.transcoding_pass.to_extension
            self.debug_log("\n target_extension: %s" % target_extension);
            target_pass_filename = "%s%s.%s" % (current_video.md5, current_pass_stack, target_extension)
            self.debug_log("\n target_pass_filename: %s" % target_pass_filename);
            target_pass_path = os.path.join(TranscoderDaemon.TMP_VIDEO_ROOT, 'transcoding', target_pass_filename)
            self.debug_log("\n target_pass_path: %s" % target_pass_path);
            self.debug_log("\n source_pass_path: %s target_pass_path: %s" % (source_pass_path, target_pass_path));
            self.debug_log("\n os.path.exists(target_pass_path): %s" % os.path.exists(target_pass_path));
            if os.path.exists(target_pass_path):
              source_pass_path = target_pass_path
              self.debug_log("\n some other transcoding job already generated the file for this pass, skip it: %s" % target_pass_path);
              continue
            else:
              command = job_pass.transcoding_pass.command.replace('$SOURCE', source_pass_path).replace('$TARGET', target_pass_path)
              self.debug_log("\n Running: %s" % command);
              command_status, command_output = commands.getstatusoutput(command)
              self.debug_log("\n command completed! %s" % command_output);
              source_pass_path = target_pass_path
          logging.info("Transcode completed, uploading result back to S3.")
          # source_url = self.put_the_result_back_in_s3(current_video, job.job_slug, target_pass_path, target_extension)
          source_url = self.put_the_result_back_in_video_tmp(current_video, job.job_slug, target_pass_path, target_extension)
          logging.info("Transcoded and uploaded video %s with the %s encoding." % (current_video.md5, job.job_slug))          
        utils.unlock_on_string(cursor, 'video_queue');
        self.debug_log("\n Wait 15 seconds...");
        time.sleep(15)
      except:
        self.debug_log("\n Error!");
        traceback.print_exc(file=sys.stdout)
        file_name = os.path.join(base, '..', 'log', 'transcoder-%s.error' % str(time.time()).replace('.', ''))
        logging.info("OMGWTFLOLBBQ: %s." % file_name)
        error_details = open(file_name, 'w')
        traceback.print_exc(file=error_details)
        error_details.close()
        if (current_video):
          current_video.status = 'pending_transcoding'
          current_video.save()
        time.sleep(15)

def main():
  AWS_CREDENTIALS = utils.load_aws_credentials(base)
  ac, sk = AWS_CREDENTIALS.S3.access_key, AWS_CREDENTIALS.S3.secret_key
  S3_CONN = S3.AWSAuthConnection(ac, sk)
  S3_URL_GENERATOR = S3.QueryStringAuthGenerator(ac, sk, is_secure=False)
  S3_URL_GENERATOR.set_expires_in(60*60*2)
  daemon_context = daemon.DaemonContext()
  # daemon_context.pidfile = lockfile.FileLock(os.path.join(base, 'pids', 'transcoder.pid'))
  # daemon_context.working_directory = base
  with daemon_context:
    transcoder = TranscoderDaemon()
    transcoder.main()

if __name__ == '__main__':
  try: main()
  except: traceback.print_exc(file=sys.stdout)