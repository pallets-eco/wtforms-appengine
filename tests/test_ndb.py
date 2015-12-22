from __future__ import unicode_literals

from wtforms.compat import text_type

from itertools import product

# This needs to stay as the first import, it sets up paths.
from gaetest_common import DummyPostData, fill_authors, NDBTestCase

from google.appengine.ext import ndb

from wtforms import Form, TextField, IntegerField, BooleanField, \
    SelectField, SelectMultipleField, FormField, FieldList

from wtforms_appengine.fields import \
    KeyPropertyField, \
    RepeatedKeyPropertyField,\
    PrefetchedKeyPropertyField,\
    RepeatedPrefetchedKeyPropertyField,\
    JsonPropertyField

from wtforms_appengine.ndb import model_form

import second_ndb_module

# Silence NDB logging
ndb.utils.DEBUG = False


GENRES = ['sci-fi', 'fantasy', 'other']


class AncestorModel(ndb.Model):
    sort = ndb.IntegerProperty()

    @classmethod
    def generate(cls):
        """
        Generate a bunch of instances that could be confused with each
        other.

        e.g.
        Key('AncestorModel', 1)
        Key('AncestorModel', 1, 'AncestorModel', 1)
        Key('AncestorModel', 1, 'AncestorModel', '1')
        Key('AncestorModel', '1')
        Key('AncestorModel', '1', 'AncestorModel', 1)
        Key('AncestorModel', '1', 'AncestorModel', '1')
        """
        ids = [1, '1', 2, '2']  # int(1) and str(1) are different ID's

        for i, parent in enumerate(ids):
            cls(id=parent, sort=-i).put()

        for i, (parent, child) in enumerate(product(ids, repeat=2)):
            parent_key = ndb.Key(cls._get_kind(), parent)
            cls(parent=parent_key, id=child, sort=i).put()

    def __unicode__(self):
        return repr(self.key.flat())


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
        self.first_author_key = self.authors[0].key

    def get_form(self, *args, **kwargs):
        form = self.F(*args, **kwargs)
        form.author.query = Author.query().order(Author.name)
        return form

    def test_no_data(self):
        form = self.get_form()

        assert not form.validate(), "Form was valid"

        ichoices = list(form.author.iter_choices())
        self.assertEqual(len(ichoices), len(self.authors))
        for author, (key, label, selected) in zip(self.authors, ichoices):
            self.assertEqual(key, KeyPropertyField._key_value(author.key))

    def test_valid_form_data(self):
        # Valid data
        data = DummyPostData(
            author=KeyPropertyField._key_value(self.first_author_key))

        form = self.get_form(data)

        assert form.validate(), "Form validation failed. %r" % form.errors

        # Check that our first author was selected
        ichoices = list(form.author.iter_choices())
        self.assertEqual(len(ichoices), len(self.authors))
        self.assertEqual(list(x[2] for x in ichoices), [True, False, False])

        self.assertEqual(form.author.data, self.first_author_key)

    def test_invalid_form_data(self):
        form = self.get_form(DummyPostData(author='fooflaf'))
        assert not form.validate()
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

        self.assertEqual(form.author.data, author.key)

    def test_populate_obj(self):
        author = Author.query().get()
        book = Book(author=author.key)
        book.put()

        form = self.F(DummyPostData(), book)

        book2 = Book()
        form.populate_obj(book2)
        self.assertEqual(book2.author, author.key)

    def test_ancestors(self):
        """
        Test that we support queries that return instances with ancestors.

        Additionally, test that when we have instances with near-identical
        ID's, (i.e. int vs str) we don't mix them up.
        """
        AncestorModel.generate()

        class F(Form):
            empty = KeyPropertyField(reference_class=AncestorModel)

        bound_form = F()

        # Iter through all of the options, and make sure that we
        # haven't returned a similar key.
        for choice_value, choice_label, selected in \
                bound_form['empty'].iter_choices():

            data_form = F(DummyPostData(empty=choice_value))
            assert data_form.validate()

            instance = data_form['empty'].data.get()
            self.assertEqual(unicode(instance), choice_label)


class TestRepeatedKeyPropertyField(NDBTestCase):
    class F(Form):
        authors = RepeatedKeyPropertyField(reference_class=Author)

    def setUp(self):
        super(TestRepeatedKeyPropertyField, self).setUp()
        self.authors = fill_authors(Author)
        self.first_author_key = self.authors[0].key
        self.second_author_key = self.authors[1].key

    def get_form(self, *args, **kwargs):
        form = self.F(*args, **kwargs)
        # See comment on KeyPropertyField.set_query as to why this is
        # bad practice.
        form.authors.query = Author.query().order(Author.name)
        return form

    def test_no_data(self):
        form = self.get_form()
        zipped = zip(self.authors, form.authors.iter_choices())

        for author, (key, label, selected) in zipped:
            self.assertFalse(selected)
            self.assertEqual(key, author.key.urlsafe())

        # Should this return None, or an empty list? AppEngine won't
        # accept None in a repeated property.
        # self.assertEqual(form.authors.data, [])

    def test_empty_form(self):
        form = self.get_form(DummyPostData(authors=[]))

        self.assertTrue(form.validate())
        self.assertEqual(form.authors.data, [])

        inst = Collab()
        form.populate_obj(inst)
        self.assertEqual(inst.authors, [])

    def test_values(self):
        data = DummyPostData(authors=[
            RepeatedKeyPropertyField._key_value(self.first_author_key),
            RepeatedKeyPropertyField._key_value(self.second_author_key)])

        form = self.get_form(data)

        assert form.validate(), "Form validation failed. %r" % form.errors
        self.assertEqual(
            form.authors.data,
            [self.first_author_key,
             self.second_author_key])

        inst = Collab()
        form.populate_obj(inst)
        self.assertEqual(
            inst.authors,
            [self.first_author_key,
             self.second_author_key])

    def test_bad_value(self):
        data = DummyPostData(authors=[
            'foo',
            RepeatedKeyPropertyField._key_value(self.first_author_key)])

        form = self.get_form(data)

        self.assertFalse(form.validate())

        # What should the data of an invalid field be?
        # self.assertEqual(form.authors.data, None)


class TestPrefetchedKeyPropertyField(TestKeyPropertyField):
    def get_form(self, *args, **kwargs):
        q = Author.query().order(Author.name)

        class F(Form):
            author = PrefetchedKeyPropertyField(query=q)

        return F(*args, **kwargs)


class TestRepeatedPrefetchedKeyPropertyField(TestRepeatedKeyPropertyField):
    def get_form(self, *args, **kwargs):
        q = Author.query().order(Author.name)

        class F(Form):
            authors = RepeatedPrefetchedKeyPropertyField(query=q)

        return F(*args, **kwargs)


class TestJsonPropertyField(NDBTestCase):
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
        zipped = zip(self.EXPECTED_AUTHOR, form())

        for (expected_name, expected_type), field in zipped:
            self.assertEqual(field.name, expected_name)
            self.assertEqual(type(field), expected_type)

    def test_book(self):
        authors = set(x.key.urlsafe() for x in fill_authors(Author))
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

    def test_choices(self):
        form = model_form(Author)
        bound_form = form()

        # Sort both sets of choices. NDB stores the choices as a frozenset
        # and as such, ends up in the wtforms field unsorted.
        expected = sorted([(v, v) for v in GENRES])

        self.assertEqual(sorted(bound_form['genre'].choices), expected)
        self.assertEqual(sorted(bound_form['genres'].choices), expected)

    def test_choices_override(self):
        """
        Check that when we provide additional choices, they override
        what was specified, or set choices on the field.
        """
        choices = ['Cat', 'Pig', 'Cow', 'Spaghetti']
        expected = [(x, x) for x in choices]

        form = model_form(Author, field_args={
            'genres': {'choices': choices},
            'name': {'choices': choices}})

        bound_form = form()

        # For provided choices, they should be in the provided order
        self.assertEqual(bound_form['genres'].choices, expected)
        self.assertEqual(bound_form['name'].choices, expected)

