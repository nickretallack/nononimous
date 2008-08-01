from wsgiref.handlers import CGIHandler as Router
from google.appengine.ext.webapp import WSGIApplication as Application
from views import *

# TODO: move to Things model
types = ('all','writing','pictures')
typor = '|'.join(types)

# URL PATTERNS:
# /find/:type/:relation/:that/:page
# /:user/:thing

routes = [
    ('/',                                     IndexView),
    ('/settings',                             SettingsView),
    (r'/data/thumbs/(.*)',                    ThumbView),
    (r'/data/files/(.*)',                     FileView),
    #('/find/',Find),  # does this one make sense?  Should find be renamed to "browse?"

    # Dynamic urls
    (r'/find/(%s)' % typor,                   TypeView),  # /find/pictures
    (r'/find/(%s)/on/([^/]*)' % typor,        OnView),    # /find/writing/on/paper
    (r'/find/(%s)/(by|for)/([^/]*)' % typor,  ByForView), # /find/music/by/beethoven
    (r'/([^/]*)',                             UserView),  # /bob
    (r'/([^/]*)/([^/]*)',                     ThingView), # /bob/picture-of-a-cat
    (r'/([^/]*)/([^/]*)/rate',                RateView),  # /bob/picture-of-a-cat/rate
    ]

if __name__ == "__main__": Router().run(Application(routes,debug=True))
