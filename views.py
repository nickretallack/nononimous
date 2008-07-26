from google.appengine.ext.webapp import RequestHandler as View
from google.appengine.ext.webapp import template
from models import *

def render(self,template_name,context={}):
  import os
  from google.appengine.api.users import create_login_url,create_logout_url
  you = context['you'] = Profile.current()
  if you: context['logout_url'] = create_logout_url(self.request.uri)
  else:   context['login_url']  = create_login_url(self.request.uri)
  path = os.path.join(os.path.dirname(__file__),"templates","%s.html" % template_name)
  self.response.out.write(template.render(path,context))

class ThumbView(View):
  def get(self,key):
    record = db.get(key)
    if record:
      self.response.headers['Content-Type'] = "image/png"
      self.response.out.write(record.thumb)
    else:
      self.error(404)
  
class FileView(View):
  def get(self,key):
    record = db.get(key)
    if record:
      self.response.headers['Content-Type'] = "image/png"
      self.response.out.write(record.file)
    else:
      self.error(404)


class IndexView(View):
  def get(self):
    "See the Front Page"
    context = {'profiles':Profile.all(),'things':Thing.all()}
    render(self,'index',context)
  def post(self):
    "Add a picture for no one"
    file  = self.request.get("file")
    Thing(poster=Profile.current(),file=file).put()
    self.redirect('/')

class SettingsView(View):
  def get(self):
    self.response.out.write("settings for %s" % Profile.current())
  def post(self):
    pass #set your settings

class UserView(View):
  def get(self,user_key):
    them = Profile.all().filter('slug =',user_key)[0]
    #pictures_by_them
    #writing_by_them
    #pictures_for_them
    #writing_for_them
    
    context = {'them':them}
    render(self,'user',context)
    
  def post(self,user_key):
    thing = Thing(poster=Profile.current(),parent_user=them,file=file).put()

class ThingView(View):
  def get(self,user_key,thing_key):
    thing = Thing.get(thing_key)
    context = {'thing':thing,'things':thing.children()}
    render(self,'thing',context)
    
  def post(self,user_key,thing_key):
    file  = self.request.get("file")
    thing = Thing.get(thing_key)
    Thing(parent=thing,poster=Profile.current(),parent_thing=thing,parent_user=thing.poster,file=file).put()
    self.redirect(thing.url())

class TypeView(View):
  def get(self,type):
    self.response.out.write("type: %s" % type)

class OnView(View):
  def get(self,type,thing_key):
    self.response.out.write("type: %s, relation: on, thing: %s" % (type,thing_key))
    
class ByForView(View):
  def get(self,type,relation,user_key):
    self.response.out.write("type: %s, relation: %s, user: %s" % (type,relation,user_key))