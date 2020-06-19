class Session(object):
  def __init__(self, domain: str=None, key: str=None, password: str=None, secret: str=None):
    self.domain = domain
    self.key = key
    self.password = password
    self.secret = secret
