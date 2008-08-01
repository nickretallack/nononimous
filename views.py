from google.appengine.ext.webapp import RequestHandler as View
from google.appengine.ext.webapp import template
from models import *

def render(self,template_name,context={}):
  import os
  from google.appengine.api.users import create_login_url,create_logout_url
  you = context['you'] = Profile.current()
  if you: context['logout_url'] = create_logout_url(self.request.uri)
  else:   context['login_url']  = create_login_url(self.request.uri)
  context['this_page'] = self.request.uri
  path = os.path.join(os.path.dirname(__file__),"templates","%s.html" % template_name)
  self.response.out.write(template.render(path,context))

def render_snippet(template_name,context={}):
  import os
  path = os.path.join(os.path.dirname(__file__),"templates","%s.html" % template_name)
  return template.render(path,context)

def make_thing(parent_thing,parent_user,text,file):
  you = Profile.current()
  if you:
    thing = Thing(parent=parent_thing,parent_thing=parent_thing,poster=you,parent_user=parent_user,text=text,file=file)
    thing.put()
    thing.update_slug()

class ThumbView(View):
  """Serves up thumbnails from database blobs"""
  def get(self,key):
    record = db.get(key)
    if record:
      self.response.headers['Content-Type'] = "image/png"
      self.response.out.write(record.thumb)
    else:
      self.error(404)
  
class FileView(View):
  """Serves up files from database blobs"""
  def get(self,key):
    record = db.get(key)
    if record:
      # TODO: use real content type
      self.response.headers['Content-Type'] = "image/png"
      self.response.out.write(record.file)
    else:
      self.error(404)

class SettingsView(View):
  def get(self):
    render(self,'settings')

  def post(self):
    you = Profile.current()
    if you:
      you.change_name(self.request.get("name"))
      you.text = self.request.get("text")
      you.put()
    self.redirect('/settings')

class IndexView(View):
  def get(self):
    "See the Front Page"
    gallery = render_snippet('gallery',{'pictures':Thing.all().order("-relevance")})
    context = {'profiles':Profile.all(),'gallery':gallery}
    render(self,'index',context)
  def post(self):
    "Add a picture for no one"
    file  = self.request.get("file")
    make_thing(None,None,None,file)
    self.redirect('/')

class UserView(View):
  def get(self,user_key):
    them = Profile.view(user_key)
    by_gallery = render_snippet('gallery',{'pictures':them.things_by()})
    for_gallery = render_snippet('gallery',{'pictures':them.things_for()})
    context = {'them':them,'by_gallery':by_gallery,'for_gallery':for_gallery}
    render(self,'user',context)
    
  def post(self,user_key):
    them = Profile.view(user_key)
    file  = self.request.get("file")
    make_thing(None,them,None,file)
    self.redirect(them.url())

ratings = ['ew','sucks','shrug','cool','awesome']

class ThingView(View):
  def get(self,user_key,thing_key):
    thing = Thing.view(thing_key)
    gallery = render_snippet('gallery',{'pictures':thing.children(),'exclude':thing})
    your_rating = Rating.gql("where thing = :1 and rater = :2",thing,Profile.current()).get()      
    context = {'thing':thing,'gallery':gallery,'rating_values':Rating.score_names,'your_rating':your_rating}
    render(self,'thing',context)
    
  def post(self,user_key,thing_key):
    thing = Thing.view(thing_key)
    file  = self.request.get("file")
    make_thing(thing,thing.poster,None,file)
    self.redirect(thing.url())

class RateView(View):
  def post(self,user_key,thing_key):
    thing = Thing.view(thing_key)
    you   = Profile.current()
    score = Rating.string_to_score(self.request.get('score'))
    if you and thing and score >= -1 and score <= 2:
      rating = Rating.gql("where thing = :1 and rater = :2",thing,you).get() or Rating(rater=you,thing=thing,score=0)
      rating.update(score)
    # raise error for cheating?  nah, just ignore it
    self.redirect(thing.url())

# TODO:
class TypeView(View):
  def get(self,type):
    self.response.out.write("type: %s" % type)

class OnView(View):
  def get(self,type,thing_key):
    self.response.out.write("type: %s, relation: on, thing: %s" % (type,thing_key))
    
class ByForView(View):
  def get(self,type,relation,user_key):
    self.response.out.write("type: %s, relation: %s, user: %s" % (type,relation,user_key))