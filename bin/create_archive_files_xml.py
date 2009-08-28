# -*- coding: utf-8 -*-

import os

IDENTIFIER = '000-079-curupira'
VIDEOS_PATH = '/Volumes/Videos/publicvideos.org/2008/000-079-curupira-derivates'
VIDEOS_TITLE = "Curupira Park — Ribeirão Preto, São Paulo, Brazil"
VIDEOS_DESCRIPTION = 'A batch of stock clips made for publicvideos.org.'
VIDEOS_LABELS = 'publicvideos.org; royalty free; free; cc0; cczero; stock footage; ace of spades'
VIDEOS_CREATOR = 'Ace of Spades'
VIDEOS_DIRECTOR = 'Ace of Spades'
VIDEOS_YEAR = '2008'
VIDEOS_UPLOADER = 'username@example.com'
VIDEOS_SPONSOR = 'username@example.com'
VIDEOS_CONTACT = 'http://fabricio.org'
VIDEOS_UPDATER = 'publicvideos'

files = os.listdir(VIDEOS_PATH)

result = '<?xml version="1.0" encoding="UTF-8"?>\n<files>\n'
for f in files:
  name = f[:-4]
  ext = f[-4:]
  if (f[0] == '.') or (ext == '.xml'):
    continue
  format = 'Ogg Video' if ext == '.OGV' else 'h.264 MPEG4'
  result = ''.join([result,'  <file name="%s" source="derivative">\n' % f])
  result = ''.join([result,'    <original>%s.MTS</original>\n' % name])
  result = ''.join([result,'    <format>%s</format>\n' % format])
  result = ''.join([result,'  </file>\n'])

result = ''.join([result, "</files>"])
filename = "%s_files.xml" % IDENTIFIER
xml = open(os.path.join(VIDEOS_PATH,filename), 'w')
xml.write(result)
xml.close()

result = '<?xml version="1.0" encoding="UTF-8"?>\n<metadata>\n'
result = ''.join([result,"  <identifier>%s</identifier>\n" % IDENTIFIER])
result = ''.join([result,"  <title>%s</title>\n" % VIDEOS_TITLE])
result = ''.join([result,"  <creator>%s</creator>\n" % VIDEOS_CREATOR])
result = ''.join([result,"  <mediatype>movies</mediatype>\n"])
result = ''.join([result,"  <collection>opensource_movies</collection>\n\n"])
result = ''.join([result,"  <description>%s</description>\n" % VIDEOS_DESCRIPTION])
result = ''.join([result,"  <year>%s</year>\n" % VIDEOS_YEAR])
result = ''.join([result,"  <subject>%s</subject>\n\n" % VIDEOS_LABELS])
result = ''.join([result,"  <uploader>%s</uploader>\n" % VIDEOS_UPLOADER])
result = ''.join([result,"  <sponsor>%s</sponsor>\n" % VIDEOS_SPONSOR])
result = ''.join([result,"  <director>%s</director>\n" % VIDEOS_DIRECTOR])
result = ''.join([result,"  <sound>sound</sound>\n"])
result = ''.join([result,"  <color>color</color>\n"])
result = ''.join([result,"  <contact>%s</contact>\n" % VIDEOS_CONTACT])
result = ''.join([result,"  <updater>%s</updater>\n" % VIDEOS_UPDATER])
result = ''.join([result,"  <licenseurl>http://creativecommons.org/publicdomain/zero/1.0/</licenseurl>\n"])
result = ''.join([result,"</metadata>"])
filename = "%s_meta.xml" % IDENTIFIER
xml = open(os.path.join(VIDEOS_PATH,filename), 'w')
xml.write(result)
xml.close()