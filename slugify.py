# Modified slugging routines originally stolen from patches to django
def slugify(value):
  """ Normalizes string, converts to lowercase, removes non-alpha characters,
  and converts spaces to hyphens.  """
  import unicodedata
  import re
  #value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
  value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
  return re.sub('[-\s]+', '-', value)

def anon_slug(value):
  import sha
  from base64 import urlsafe_b64encode
  return urlsafe_b64encode(sha.new(value).digest())

#import sha
#from base64 import urlsafe_b64encode
#emails = ["nickretallack@gmail.com","foobar@gmail.com","stewbar@gmail.com","lalala@gmail.com"]
#for email in emails:
#  print urlsafe_b64encode(sha.new(email).digest())
#print slugify(u"Big Bad bob's Garage")

