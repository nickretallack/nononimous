from google.appengine.ext import db
from datetime import datetime
import time

"I guess this is the best way to get a date from a string in python..."
the_beginning = datetime.fromtimestamp(time.mktime(time.strptime('Mon Jul 28 05:24:08 2008')))

"""Nononimous might be a good name for this site, as it's a lot like anonymous sites, except
it isn't.  You get a reputation and a profile page with all your stuff"""

class Profile(db.Model):
  """Local representation of a user.  This should be used instead of User whenever possible,
  because it is a normal model describing only users who have used this app, and is not restricted
  in access.  A profile is created automatically if it doesn't already exist, any time a user loads
  a page that needs to know if they are logged in."""

  def __init__(self,*args,**kwargs):
    super(Profile, self).__init__(*args, **kwargs)
    self.change_name(self.name)

  user = db.UserProperty()
  name = db.StringProperty()
  text = db.TextProperty()

  "Generated"
  slug = db.StringProperty()

  def change_name(self,name):
    """Should probably exclude some reserved words here:
    styles, images, scripts (group these under 'static'?)
    data (for generated stuff)
    settings...
    """
    from slugify import slugify
    self.name = name
    new_slug = slugify(name)
    if self.slug != new_slug:
      doppelganger = Profile.gql("where slug = :1",new_slug).get()
      if doppelganger: raise "OH NO"
      self.slug = new_slug

  def __str__(self): return self.name

  def url(self): return "/%s" % self.slug
  def thumb_url(self):
    import md5
    hash = md5.new(self.user.email()).hexdigest()
    return "http://www.gravatar.com/avatar/%s?s=150&d=monsterid&r=x" % hash

  @classmethod
  def current(cls):
    "Looks up the user's profile, and creates it if it doesn't exist"
    from google.appengine.api.users import get_current_user
    user = get_current_user()
    if user:
      return Profile.gql("where user = :1", user).get() or Profile(user=user,name=user.nickname()).put()

  @classmethod
  def view(cls,slug):
    return Profile.gql("where slug = :1",slug).get()
    
  def things_for(self):
    return Thing.gql("where parent_user = :1 and poster != :1",self).fetch(50)
  
  def things_by(self):
    return Thing.gql("where poster = :1",self).fetch(50)

"""Totally messy, but i couldn't find a better way..."""
def flickr_thumb(file,size):
  from google.appengine.api import images
  from zopeimage import getImageInfo
  type,width,height = getImageInfo(file)
  if width < height: 
    file = images.resize(file,width=size)
    type,width,height = getImageInfo(file)
    cropoff = ((height - size)*.5)/height
    file = images.crop(file,top_y=cropoff,bottom_y=1.0 - cropoff,left_x=0.0,right_x=1.0)
  else:
    file = images.resize(file,height=size)
    type,width,height = getImageInfo(file)
    cropoff = ((width - size)*.5)/width
    file = images.crop(file,left_x=cropoff,right_x=1.0 - cropoff,top_y=0.0,bottom_y=1.0)
  return file
  

class Thing(db.Expando):
  """Something a user has uploaded.  """

  @classmethod
  def ancestor_attribute(cls,depth):
    return "ancestor%s" % depth


  def __init__(self,*args,**kwargs):
    super(Thing, self).__init__(*args, **kwargs)
    
    if self.file:
      self.thumb = flickr_thumb(self.file,150)
      
    days_new = (datetime.now() - the_beginning).days
    self.relevance = self.score + days_new
    
  # Convention: all update_* methods call self.put()
  def update_slug(self):
    self.slug = str(self.key().id())
    self.put()
    
  def update_score(self,score_delta):
    """Only to be called by Rating.update"""
    self.score += score_delta
    self.relevance += score_delta
    self.put()
    
  "The Meat"
  text          = db.TextProperty()
  file          = db.BlobProperty(default=None)

  "Associations"
  poster        = db.ReferenceProperty(Profile, collection_name="out_job_set", required=True)
  parent_user   = db.ReferenceProperty(Profile, collection_name="in_job_set")
  parent_thing  = db.SelfReferenceProperty()  # NOTE: can we use the builtin parent column?

  "Generated -- DON'T TOUCH"
  slug          = db.StringProperty()
  thumb         = db.BlobProperty(default=None)
  created       = db.DateTimeProperty(auto_now_add=True)
  score  = db.IntegerProperty(default=0)
  relevance = db.IntegerProperty()

  """Perhaps we should store content type as well, as we do need to create a request handler
  to serve this file content out of the database on a normal webpage.  I wonder how page-embedded
  data works on the web though, like the sort you find in doc to html conversions?"""

  def url(self):
    return "/%s/%s" % (self.poster.slug,self.slug)
    
  def file_url(self):
    return "/data/files/%s" % self.key()
    
  def thumb_url(self):
    return "/data/thumbs/%s" % self.key()

  @classmethod
  def view(cls,slug):
    return Thing.gql("where slug = :1",slug).get()

  def children(self):
    return Thing.gql("where ancestor is :1 order by relevance desc",self)
    
  def child_pictures(self): # doesn't work
    self.children().filter("file !=", None)
    

class Rating(db.Model):
  score_names = ['ew','sucks','shrug','cool','awesome']
  
  @classmethod
  def string_to_score(cls,string):
    return cls.score_names.index(string) - cls.score_names.index('shrug')

  def string(self):
    return self.score_names[self.score + self.score_names.index('shrug')]
  
  "Users can rate things"
  thing = db.ReferenceProperty(Thing)
  rater = db.ReferenceProperty(Profile)
  score = db.IntegerProperty()
  
  #def __init__(self,*args,**kwargs):
  #  super(Rating, self).__init__(*args, **kwargs)
  #  self.update(self.score) # todo: refactor this!
  
  def update(self,new_score):
    # TODO: trying to decide if this should take a string or an integer 
    #if new_score_string in self.score_names:
    #self.string_to_score(new_score_string)
    score_delta = new_score - self.score
    self.thing.update_score(score_delta)
    self.score = new_score
    self.put()
