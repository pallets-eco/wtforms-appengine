from __future__ import unicode_literals

# This needs to stay as the first import, it sets up paths.
from gaetest_common import DummyPostData, fill_authors, NDBTestCase

from google.appengine.ext import ndb
from wtforms import Form, TextField, IntegerField, BooleanField
from wtforms.compat import text_type
from wtforms_appengine.fields import JsonPropertyField, KeyPropertyField
from wtforms_appengine.ndb import model_form

import second_ndb_module


class Author(ndb.Model):
    name = ndb.StringProperty(required=True)
    city = ndb.StringProperty()
    age = ndb.IntegerProperty(required=True)
    is_admin = ndb.BooleanProperty(default=False)


class Book(ndb.Model):
    author = ndb.KeyProperty(kind=Author)


class TestJsonPropertyField(NDBTestCase):
    nosegae_datastore_v3 = True

    class F(Form):
        field = JsonPropertyField()

    def test_round_trip(self):
        # Valid data
        test_data = {u'a': {'b': 3, 'c': ['a', 1, False]}}

        form = self.F()
        form.process(data={'field': test_data})
        raw_string = form.field._value()
        assert form.validate()
        form2 = self.F()
        form2.process(formdata=DummyPostData(field=raw_string))
        assert form.validate()
        # Test that we get back the same structure we serialized
        self.assertEqual(test_data, form2.field.data)


class TestKeyPropertyField(NDBTestCase):
    nosegae_datastore_v3 = True

    class F(Form):
        author = KeyPropertyField(reference_class=Author)

    def setUp(self):
        super(TestKeyPropertyField, self).setUp()

        self.authors = fill_authors(Author)
        self.first_author_id = self.authors[0].key.id()

    def tearDown(self):
        for author in Author.query():
            author.key.delete()

    def test_no_data(self):
        form = self.F()
        form.author.query = Author.query().order(Author.name)

        assert not form.validate()
        ichoices = list(form.author.iter_choices())
        self.assertEqual(len(ichoices), len(self.authors))
        for author, (key, label, selected) in zip(self.authors, ichoices):
            self.assertEqual(key, text_type(author.key.id()))

    def test_form_data(self):
        # Valid data
        form = self.F(DummyPostData(author=text_type(self.first_author_id)))
        form.author.query = Author.query().order(Author.name)
        assert form.validate()
        ichoices = list(form.author.iter_choices())
        self.assertEqual(len(ichoices), len(self.authors))
        self.assertEqual(list(x[2] for x in ichoices), [True, False, False])

        # Bogus Data
        form = self.F(DummyPostData(author='fooflaf'))
        assert not form.validate()
        print list(form.author.iter_choices())
        assert all(x[2] is False for x in form.author.iter_choices())


class TestModelForm(NDBTestCase):
    nosegae_datastore_v3 = True

    EXPECTED_AUTHOR = [
        ('name', TextField),
        ('city', TextField),
        ('age', IntegerField),
        ('is_admin', BooleanField)]

    def test_author(self):
        form = model_form(Author)
        zipped = zip(self.EXPECTED_AUTHOR, form())

        for (expected_name, expected_type), field in zipped:
            self.assertEqual(field.name, expected_name)
            self.assertEqual(type(field), expected_type)

    def test_book(self):
        authors = set(text_type(x.key.id()) for x in fill_authors(Author))
        authors.add('__None')
        form = model_form(Book)
        keys = set()
        for key, b, c in form().author.iter_choices():
            keys.add(key)

        self.assertEqual(authors, keys)

    def test_second_book(self):
        authors = set(text_type(x.key.id()) for x in fill_authors(Author))
        authors.add('__None')
        form = model_form(second_ndb_module.SecondBook)
        keys = set()
        for key, b, c in form().author.iter_choices():
            keys.add(key)

        self.assertEqual(authors, keys)
