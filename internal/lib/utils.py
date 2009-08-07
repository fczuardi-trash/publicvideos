class jshash(dict):
  def __getattr__(self, k):
    if self.has_key(k): return self[k]
    raise AttributeError, repr(k)
  def __setattr__(self, k, v): self[k] = v
  def __delattr__(self, k): del self[k]
  def __enter__(self): return self
  def __exit__(self, type, value, tv): pass
  
def lock_on_string(cur, string, timeout=1000):
  cur.execute('select get_lock(%s, %s);', (string, timeout))
  return cur.fetchone()

def unlock_on_string(cur, string):
  cur.execute('select release_lock(%s);', (string,))
  return cur.fetchone()
  
def unlock_and_lock_again_real_quick(cur, string, timeout=100):
  unlock_on_string(cur, string)
  lock_on_string(cur, string, timeout)
  
def load_aws_credentials(base):
  AWS_CREDENTIALS = utils.jshash({'S3':jshash()})
  config_file = os.path.join(base, os.path.pardir, 'config', 'aws.conf')
  parsed_config = ConfigParser.ConfigParser()
  parsed_config.read(config_file)
  for section in parsed_config.sections():
    service = section.split(':')[1]
    if service == 's3':
      AWS_CREDENTIALS.S3.access_key = parsed_config.get(section, 'access_key')
      AWS_CREDENTIALS.S3.secret_key = parsed_config.get(section, 'secret_key')
  return AWS_CREDENTIALS
