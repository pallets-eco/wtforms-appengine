from google.cloud import ndb


class SecondBook(ndb.Model):
    author = ndb.KeyProperty(kind='Author')
