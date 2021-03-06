from templatehandler import TemplateHandler
from entities import WikiPage
from json_utils import DateTimeEncoder
import webapp2, json, datetime, math
from google.appengine.api import memcache
from google.appengine.ext import db

class WikiPageHandler(TemplateHandler):
    templatename = 'wiki.html'
    def get(self, page_url):
        page = None
        lastUpdate = None
        version = 0
        if not self.request.get("version") or not self.request.get("version").isdigit():
            page = memcache.get(page_url)
            lastUpdate = memcache.get('lastUpdate_'+page_url)
        else:
            version=int(self.request.get("version"))-1
        
        #no cache hit or specific version requested
        if not page or not lastUpdate:
            page_query = WikiPage.query(WikiPage.url == page_url).order(-WikiPage.date)
            wiki_page_object = page_query.fetch()
            print version, len(wiki_page_object)
            if (version >= len(wiki_page_object) and len(wiki_page_object)>0) or version<0:
                self.redirect(page_url)
                return
            
            if len(wiki_page_object)==0:
                self.redirect("/_edit"+page_url)
                return
            page = wiki_page_object[version].content
            memcache.add(page_url,page)
            lastUpdate = datetime.datetime.now()
            memcache.add('lastUpdate_'+page_url,lastUpdate)
            
        age = int(math.ceil((datetime.datetime.now() - lastUpdate).total_seconds()-1))    
        ageString = 'Queried {} seconds ago'.format(age)
        template_values = {'content': page, 'id':page_url, 'age': ageString,'editlink':"/_edit"+page_url, 'historylink':"/_history"+page_url}
        self.render(self.templatename, template_values)
        
        
class PermalinkJson(webapp2.RequestHandler):
    def get(self, post_id):
        post = BlogPost.get_by_id(int(post_id))
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(post.to_dict(), cls=DateTimeEncoder))