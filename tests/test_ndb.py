from wtforms.compat import text_type

from itertools import product

# This needs to stay as the first import, it sets up paths.
from .gaetest_common import DummyPostData, fill_authors

from google.cloud import ndb

from wtforms import Form, StringField, IntegerField, BooleanField, \
    SelectField, SelectMultipleField, FormField, FieldList

from wtforms_appengine.fields import \
    KeyPropertyField, \
    RepeatedKeyPropertyField,\
    PrefetchedKeyPropertyField,\
    RepeatedPrefetchedKeyPropertyField,\
    JsonPropertyField, \
    StringListPropertyField, \
    GeoPtPropertyField, \
    IntegerListPropertyField, \
    ReferencePropertyField

from wtforms_appengine.ndb import model_form

from . import second_ndb_module

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


class TestKeyPropertyField:
    class F(Form):
        author = KeyPropertyField(reference_class=Author)

    def setUp(self):
        self.authors = fill_authors(Author)
        self.first_author_key = self.authors[0].key

    def get_form(self, *args, **kwargs):
        form = self.F(*args, **kwargs)
        form.author.query = Author.query().order(Author.name)
        return form

    def test_no_data(self, client):
        with client.context():
            self.setUp()
            form = self.get_form()
            assert not form.validate(), "Form was valid"

            ichoices = list(form.author.iter_choices())

            assert len(ichoices) == len(self.authors)
            for author, (key, label, selected) in zip(self.authors, ichoices):
                assert key == KeyPropertyField._key_value(author.key)

    def test_valid_form_data(self, client):
        with client.context():
            self.setUp()
            # Valid data
            data = DummyPostData(
                author=KeyPropertyField._key_value(self.first_author_key))

            form = self.get_form(data)
            assert form.validate(), "Form validation failed. %r" % form.errors

            # Check that our first author was selected
            ichoices = list(form.author.iter_choices())

            assert len(ichoices) == len(self.authors)
            assert [x[2] for x in ichoices] == [True, False, False]

            assert form.author.data == self.first_author_key

    def test_invalid_form_data(self, client):
        with client.context():
            self.setUp()
            form = self.get_form(DummyPostData(author='fooflaf'))
            assert not form.validate()
            assert all(x[2] is False for x in form.author.iter_choices())

    def test_obj_data(self, client):
        """
        When creating a form from an object, check that the form will render
        (hint: it didn't before)
        """
        with client.context():
            self.setUp()
            author = Author.query().get()
            book = Book(author=author.key)
            book.put()

            form = self.F(DummyPostData(), book)

            str(form.author)

        assert form.author.data == author.key

    def test_populate_obj(self, client):
        with client.context():
            self.setUp()
            author = Author.query().get()
            book = Book(author=author.key)
            book.put()

            form = self.F(DummyPostData(), book)

            book2 = Book()
            form.populate_obj(book2)
        assert book2.author == author.key

    def test_ancestors(self, client):
        """
        Test that we support queries that return instances with ancestors.

        Additionally, test that when we have instances with near-identical
        ID's, (i.e. int vs str) we don't mix them up.
        """
        with client.context():
            AncestorModel.generate()

            class F(Form):
                empty = KeyPropertyField(reference_class=AncestorModel)

            bound_form = F()

            # Iter through all of the options, and make sure that we
            # haven't returned a similar key.
            for choice_value, choice_label, selected in \
                    bound_form.empty.iter_choices():

                data_form = F(DummyPostData(empty=choice_value))
                assert data_form.validate()

                instance = data_form.empty.data.get()
                assert str(instance) == choice_label


class TestRepeatedKeyPropertyField:
    class F(Form):
        authors = RepeatedKeyPropertyField(reference_class=Author)

    def setUp(self):
        self.authors = fill_authors(Author)
        self.first_author_key = self.authors[0].key
        self.second_author_key = self.authors[1].key

    def get_form(self, *args, **kwargs):
        form = self.F(*args, **kwargs)
        # See comment on KeyPropertyField.set_query as to why this is
        # bad practice.
        form.authors.query = Author.query().order(Author.name)
        return form

    def test_no_data(self, client):
        with client.context():
            self.setUp()
            form = self.get_form()
            zipped = zip(self.authors, form.authors.iter_choices())

            for author, (key, label, selected) in zipped:
                assert selected is False
                assert key == author.key.urlsafe()

        # Should this return None, or an empty list? AppEngine won't
        # accept None in a repeated property.
        # assert form.authors.data == []

    def test_empty_form(self, client):
        with client.context():
            self.setUp()
            form = self.get_form(DummyPostData(authors=[]))
            assert form.validate() is True

            assert form.authors.data == []

            inst = Collab()
            form.populate_obj(inst)
            assert inst.authors == []

    def test_values(self, client):
        with client.context():
            self.setUp()
            data = DummyPostData(authors=[
                RepeatedKeyPropertyField._key_value(self.first_author_key),
                RepeatedKeyPropertyField._key_value(self.second_author_key)])

            form = self.get_form(data)
            assert form.validate(), "Form validation failed. %r" % form.errors
            authors = [self.first_author_key, self.second_author_key]
            assert form.authors.data == authors

            inst = Collab()
            form.populate_obj(inst)
            assert inst.authors == [self.first_author_key, self.second_author_key]

    def test_bad_value(self, client):
        with client.context():
            self.setUp()
            data = DummyPostData(authors=[
                'foo',
                RepeatedKeyPropertyField._key_value(self.first_author_key)])

            form = self.get_form(data)
            assert form.validate() is False

            # What should the data of an invalid field be?
            # assert form.authors.data is None


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


class TestJsonPropertyField:
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
        assert test_data == form2.field.data


class TestModelForm:
    EXPECTED_AUTHOR = [
        ('age', IntegerField),
        ('city', StringField),
        ('genre', SelectField),
        ('genres', SelectMultipleField),
        ('is_admin', BooleanField),
        ('name', StringField),
        ('address', FormField),
        ('address_history', FieldList),
    ]

    def test_author(self, client):
        with client.context():
            form = model_form(Author)
        x = form()
        zipped = zip(self.EXPECTED_AUTHOR, x)

        for (expected_name, expected_type), field in zipped:
            assert field.name == expected_name
            assert type(field) == expected_type

    def test_book(self, client):
        with client.context():
            authors = set(x.key.urlsafe() for x in fill_authors(Author))
            authors.add('__None')
            form = model_form(Book)
            keys = set()
            for key, b, c in form().author.iter_choices():
                keys.add(key)

        assert authors == keys

    def test_second_book(self, client):
        with client.context():
            authors = set(text_type(x.key.id()) for x in fill_authors(Author))
            authors.add('__None')
            form = model_form(second_ndb_module.SecondBook)
            keys = set()
            for key, b, c in form().author.iter_choices():
                keys.add(key)

        assert authors != keys

    def test_choices(self, client):
        form = model_form(Author)
        bound_form = form()

        # Sort both sets of choices. NDB stores the choices as a frozenset
        # and as such, ends up in the wtforms field unsorted.
        expected = sorted([(v, v) for v in GENRES])

        assert sorted(bound_form.genre.choices) == expected
        assert sorted(bound_form.genres.choices) == expected

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
        assert bound_form.genres.choices == expected
        assert bound_form.name.choices == expected


class TestGeoFields:
    class GeoTestForm(Form):
        geo = GeoPtPropertyField()

    def test_geopt_property(self):
        form = self.GeoTestForm(DummyPostData(geo='5.0, -7.0'))
        assert form.validate()
        assert form.geo.data == '5.0,-7.0'
        form = self.GeoTestForm(DummyPostData(geo='5.0,-f'))
        assert not form.validate()


class TestReferencePropertyField:
    nosegae_datastore_v3 = True

    def build_form(self, reference_class=Author, **kw):
        class BookForm(Form):
            author = ReferencePropertyField(
                reference_class=reference_class,
                **kw)
        return BookForm

    def author_expected(self, selected_index=None, get_label=lambda x: x.name):
        expected = set()
        for i, author in enumerate(self.authors):
            expected.add((author.key.urlsafe(),
                          get_label(author),
                          i == selected_index))
        return expected

    def setUp(self):
        self.authors = fill_authors(Author)
        self.author_names = set(x.name for x in self.authors)
        self.author_ages = set(x.age for x in self.authors)

    def test_basic(self, client):
        with client.context():
            self.setUp()
            F = self.build_form(
                get_label='name'
            )
            form = F()
            assert set(form.author.iter_choices()) == self.author_expected()
            assert not form.validate()

            form = F(DummyPostData(author=str(self.authors[0].key)))
            assert form.validate()
            # What we want to validate here?
            # assert set(form.author.iter_choices()) == self.author_expected(0)

    def test_not_in_query(self, client):
        with client.context():
            self.setUp()
            F = self.build_form()
            new_author = Author(name='Jim', age=48)
            new_author.put()
            form = F(author=new_author)
            form.author.query = Author.query().filter(Author.name != 'Jim')
            assert form.author.data is new_author
            assert not form.validate()

    def test_get_label_func(self, client):
        with client.context():
            self.setUp()
            get_age = lambda x: x.age
            F = self.build_form(get_label=get_age)
            form = F()
            ages = set(x.label.text for x in form.author)
            assert ages == self.author_ages

    def test_allow_blank(self, client):
        with client.context():
            self.setUp()
            F = self.build_form(allow_blank=True, get_label='name')
            form = F(DummyPostData(author='__None'))
            assert form.validate()
            assert form.author.data is None
            expected = self.author_expected()
            expected.add(('__None', '', True))
            assert set(form.author.iter_choices()) == expected


class TestStringListPropertyField:
    class F(Form):
        a = StringListPropertyField()

    def test_basic(self, client):
        with client.context():
            form = self.F(DummyPostData(a='foo\nbar\nbaz'))
            assert form.a.data == ['foo', 'bar', 'baz']
            assert form.a._value() == 'foo\nbar\nbaz'
