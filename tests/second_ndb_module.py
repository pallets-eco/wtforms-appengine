from google.appengine.ext import ndb

class SecondBook(ndb.Model):
    author = ndb.KeyProperty(kind='Author')
