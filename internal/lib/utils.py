class jshash(dict):
  def __getattr__(self, k):
    if self.has_key(k): return self[k]
    raise AttributeError, repr(k)
  def __setattr__(self, k, v): self[k] = v
  def __delattr__(self, k): del self[k]
  def __enter__(self): return self
  def __exit__(self, type, value, tv): pass
  
def lock_on_string(cur, string, timeout):
  cur.execute('select get_lock(%s, %s);', (string, timeout))
  return cur.fetchone()

def unlock_on_string(cur, string):
  cur.execute('select release_lock(%s);', (string,))
  return cur.fetchone()