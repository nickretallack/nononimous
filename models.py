from google.appengine.ext import db

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
  name = db.StringProperty() # Not used yet, but soon will be.  We don't want to give away your email

  "Generated"
  slug = db.StringProperty()

  def change_name(self,name):
    from slugify import slugify
    self.name = name
    self.slug = slugify(name)

  def __str__(self): return self.name

  "url currently only returns anonymous user urls, but will soon put your name in em"
  #def url(self): return "/users/"+str(self.key.id)+"/"
  def url(self): return "/%s" % self.slug

  @classmethod
  def current(cls):
    "Looks up the user's profile, and creates it if it doesn't exist"
    from google.appengine.api.users import get_current_user
    user = get_current_user()
    if user:
      return Profile.gql("where user = :1", user).get() or Profile(user=user,name=user.nickname()).put()
      #profile = Profile.gql("where user = :1", user).get() or make_profile(user)
      #if not profile:
      #  profile = make_profile(user)
      #return profile

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
    # NOTE: lets exclude parent_thing from this model, and just use ancestors or something?
    # or the builtin parent key
    if self.parent_thing:
      "We've got a parent.  Lets check its depth and replicate its ancestors"
      self.depth = self.parent_thing.depth + 1

      # copying attributes
      for depth in xrange(self.parent_thing.depth):
        attribute = self.ancestor_attribute(depth)
        setattr(self, attribute, getattr(self.parent_thing,attribute))
      
      setattr(self, self.ancestor_attribute(self.parent_thing.depth), self.parent_thing.key().id())
      
    else: self.depth = 0
    
    if self.file:
      self.thumb = flickr_thumb(self.file,150)
    
    
  "The Meat"
  text          = db.TextProperty()
  file          = db.BlobProperty(default=None)

  "Associations"
  poster        = db.ReferenceProperty(Profile, collection_name="out_job_set", required=True)
  parent_user   = db.ReferenceProperty(Profile, collection_name="in_job_set")
  parent_thing  = db.SelfReferenceProperty()  # NOTE: can we use the builtin parent column?

  "Generated -- DON'T TOUCH"
  #slug          = db.StringProperty()
  thumb         = db.BlobProperty(default=None)
  created       = db.DateTimeProperty(auto_now_add=True)
  cached_score  = db.IntegerProperty(default=0)
  cached_relevance = db.IntegerProperty()
  depth         = db.IntegerProperty()
  # ancestor keys also generated

  """Perhaps we should store content type as well, as we do need to create a request handler
  to serve this file content out of the database on a normal webpage.  I wonder how page-embedded
  data works on the web though, like the sort you find in doc to html conversions?"""

  """As usual this is the anonymous version.  Named version coming later.
  I think we'll need a slug field in these models."""
  #def url(self): return "/users/"+self.doer.key.id+"/jobs/"+self.key.id+"/"
  #def url(self): return "/%s/%s" % (self.poster.slug,self.slug)
  #def url(self): return "/%s/%s" % (self.poster.slug,self.pk)
  def url(self): return "/%s/%s" % (self.poster.slug,self.key())
  def file_url(self): return "/data/files/%s" % self.key()
  def thumb_url(self): return "/data/thumbs/%s" % self.key()

  def children(self):
    return Thing.all().ancestor(self)
    #return Thing.all().filter("%s =" % self.ancestor_attribute(self.depth), self.key().id()) #.order("relevance")
    
  #def child_pictures(self):
  #return self.children().


class Rating(db.Model):
  "Users can rate things"
  thing = db.ReferenceProperty(Thing)
  rater = db.ReferenceProperty(Profile)
  score = db.RatingProperty()

