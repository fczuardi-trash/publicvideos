import os
from ftplib import FTP

FTP_USERNAME = 'username@example.org'
FTP_PASSWORD = 'XXXXX'
IDENTIFIER = 'an-unique-ftp-folder-name'
VIDEOS_PATH = '/path/to/your/files'


ftp = FTP('items-uploads.archive.org')
ftp.login(FTP_USERNAME, FTP_PASSWORD)

try:
  ftp.mkd(IDENTIFIER)
except:
  pass

ftp.cwd(IDENTIFIER)

files = os.listdir(VIDEOS_PATH)
for file_name in files:
  if (file_name[0] == '.'):
    continue
  f = open(os.path.join(VIDEOS_PATH, file_name),  'rb', 1024)
  ftp.storbinary('STOR %s' % file_name, f)

ftp.close()