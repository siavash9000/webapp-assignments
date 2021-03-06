from templatehandler import TemplateHandler
from entities import WikiPage;
from google.appengine.api import memcache           
import datetime
class EditHandler(TemplateHandler):
    templatename = 'edit.html'
    def get(self, url):   
        version = 0
        print self.request.get("version")
        if self.request.get("version") and self.request.get("version").isdigit():
             version = int(self.request.get("version"))-1
        if version<0 or (version>=self.getNumberOfVersions(url) and self.getNumberOfVersions(url)):
            self.redirect(url)
            return
        template_values = {"action": "/_edit"+url,"content":self.getContent(url,version)}  
        print template_values
        print version
        self.render(self.templatename,template_values)

    def post(self,url):
        content = self.request.get("content")        
        if (not content):
            template_values = {"error": "Please enter content.","content":content}
            self.render(self.templatename,template_values)
        else:
            self.persist(url,content)
            self.redirect(url)
    
    def persist(self, url,content):
        newPage = WikiPage()
        newPage.url = url
        newPage.content = content
        newPage.put()
        if memcache.get(url):
            memcache.replace(url,content)
            lastUpdate = datetime.datetime.now()
            memcache.replace('lastUpdate_'+url,lastUpdate)
        else:
            memcache.add(url,content)
            lastUpdate = datetime.datetime.now()
            memcache.add('lastUpdate_'+url,lastUpdate)
            
    def getNumberOfVersions(self,url):
        page_query = WikiPage.query(WikiPage.url == url)
        return len(page_query.fetch())
    
    def getContent(self,url,version):
        page_query = WikiPage.query(WikiPage.url == url).order(-WikiPage.date)
        page = page_query.fetch()
        if len(page)==0:
            return ''
        else:
            return page[version].content