from __future__ import unicode_literals

# This needs to stay as the first import, it sets up paths.
from .gaetest_common import DummyPostData, fill_authors
from .base import NDBTestCase
from google.appengine.ext import ndb
from wtforms_appengine import model_form

from wtforms import Form, TextField, IntegerField, BooleanField, \
    SelectField, SelectMultipleField, FormField, FieldList
from wtforms.compat import text_type
from wtforms_ndb.fields import \
    KeyPropertyField, \
    RepeatedKeyPropertyField,\
    PrefetchedKeyPropertyField

ndb.utils.DEBUG = False

GENRES = ['sci-fi', 'fantasy', 'other']

class Address(ndb.Model):
    line_1 = ndb.StringProperty()
    line_2 = ndb.StringProperty()
    city = ndb.StringProperty()
    country = ndb.StringProperty()


class Author(ndb.Model):
    name = ndb.StringProperty(required=True)
    city = ndb.StringProperty()
    age = ndb.IntegerProperty(required=True)
    is_admin = ndb.BooleanProperty(default=False)

    # Test both repeated choice-fields and non-repeated.
    genre = ndb.StringProperty(choices=GENRES)
    genres = ndb.StringProperty(choices=GENRES, repeated=True)

    address = ndb.StructuredProperty(Address)
    address_history = ndb.StructuredProperty(Address, repeated=True)


class Book(ndb.Model):
    author = ndb.KeyProperty(kind=Author)


class Collab(ndb.Model):
    authors = ndb.KeyProperty(kind=Author, repeated=True)


class TestKeyPropertyField(NDBTestCase):
    class F(Form):
        author = KeyPropertyField(reference_class=Author)

    def setUp(self):
        super(TestKeyPropertyField, self).setUp()
        self.authors = fill_authors(Author)
        self.first_author_id = self.authors[0].key.id()

    def get_form(self, *args, **kwargs):
        form = self.F(*args, **kwargs)
        form.author.query = Author.query().order(Author.name)
        return form

    def test_no_data(self):
        form = self.get_form()

        assert not form.validate()
        ichoices = list(form.author.iter_choices())
        self.assertEqual(len(ichoices), len(self.authors))
        for author, (key, label, selected) in zip(self.authors, ichoices):
            self.assertEqual(key, text_type(author.key.id()))

    def test_form_data(self):
        # Valid data
        form = self.get_form(DummyPostData(author=text_type(self.first_author_id)))

        assert form.validate()
        ichoices = list(form.author.iter_choices())
        self.assertEqual(len(ichoices), len(self.authors))
        self.assertEqual(list(x[2] for x in ichoices), [True, False, False])

        # Bogus Data
        form = self.get_form(DummyPostData(author='fooflaf'))
        assert not form.validate()
        print list(form.author.iter_choices())
        assert all(x[2] is False for x in form.author.iter_choices())

    def test_obj_data(self):
        """
        When creating a form from an object, check that the form will render
        (hint: it didn't before)
        """
        author = Author.query().get()
        book = Book(author=author.key)
        book.put()

        form = self.F(DummyPostData(), book)

        str(form['author'])

    def test_populate_obj(self):
        author = Author.query().get()
        book = Book(author=author.key)
        book.put()

        form = self.F(DummyPostData(), book)

        book2 = Book()
        form.populate_obj(book2)
        self.assertEqual(book2.author, author.key)


class TestRepeatedKeyPropertyField(NDBTestCase):
    class F(Form):
        authors = RepeatedKeyPropertyField(reference_class=Author)

    def setUp(self):
        super(TestRepeatedKeyPropertyField, self).setUp()
        self.authors = fill_authors(Author)
        self.first_author_id = self.authors[0].key.id()
        self.second_author_id = self.authors[1].key.id()

    def get_form(self, *args, **kwargs):
        form = self.F(*args, **kwargs)
        form.authors.query = Author.query().order(Author.name)
        return form

    def test_no_data(self):
        form = self.get_form()
        for author, (key, label, selected) in zip(self.authors, form.authors.iter_choices()):
            self.assertFalse(selected)
            self.assertEqual(key, text_type(author.key.id()))

    def test_empty_form(self):
        form = self.get_form(DummyPostData(authors=[]))
        self.assertTrue(form.validate())

        inst = Collab()
        form.populate_obj(inst)
        self.assertEqual(inst.authors, [])

    def test_values(self):
        data = DummyPostData(authors=[
            str(self.first_author_id),
            str(self.second_author_id)])

        form = self.get_form(data)
        self.assertTrue(form.validate())

        inst = Collab()
        form.populate_obj(inst)
        self.assertEqual(inst.authors,[
            ndb.Key(Author, self.first_author_id),
            ndb.Key(Author, self.second_author_id)])

    def test_bad_value(self):
        data = DummyPostData(authors=['foo'])
        form = self.get_form(data)
        self.assertFalse(form.validate())


class TestPrefetchedKeyPropertyField(TestKeyPropertyField):
    def get_form(self, *args, **kwargs):
        class F(Form):
            author = PrefetchedKeyPropertyField(
                    query = Author.query().order(Author.name))

        return F(*args, **kwargs)


class TestModelForm(NDBTestCase):
    EXPECTED_AUTHOR = [
        ('name', TextField),
        ('city', TextField),
        ('age', IntegerField),
        ('is_admin', BooleanField),
        ('genre', SelectField),
        ('genres', SelectMultipleField),
        ('address', FormField),
        ('address_history', FieldList),
    ]

    def test_author(self):
        form = model_form(Author)
        for (expected_name, expected_type), field in zip(self.EXPECTED_AUTHOR, form()):
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

    def test_choices(self):
        form = model_form(Author)
        bound_form = form()

        # Sort both sets of choices. NDB stores the choices as a frozenset
        # and as such, ends up in the wtforms field unsorted.
        expected = sorted([(v,v) for v in GENRES])

        self.assertEqual(sorted(bound_form['genre'].choices), expected)
        self.assertEqual(sorted(bound_form['genres'].choices), expected)
