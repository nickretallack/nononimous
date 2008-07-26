from wsgiref.handlers import CGIHandler as Router
from google.appengine.ext.webapp import WSGIApplication as Application
from views import *

types = ('all','writing','pictures')
typor = '|'.join(types)

# URL TYPES:
# /find/:type/:relation/:that/:page
# /:user/:thing

routes = [
    ('/',IndexView),
    ('/settings',SettingsView),
    (r'/data/thumbs/(.*)',ThumbView),
    (r'/data/files/(.*)',FileView),
    #('/find/',Find),  # does this one make sense?  Should find be renamed to "browse?"
    (r'/find/(%s)' % typor,TypeView),
    (r'/find/(%s)/on/([^/]*)' % typor,OnView),
    (r'/find/(%s)/(by|for)/([^/]*)' % typor,ByForView),
    (r'/([^/]*)',UserView),           # /bob
    (r'/([^/]*)/([^/]*)',ThingView), #/bob/picture-of-a-cat
    ]

if __name__ == "__main__": Router().run(Application(routes,debug=True))
