from google.appengine.ext import ndb

import wtforms
from wtforms_appengine import model_form

from .base import NDBTestCase

ndb.utils.DEBUG = False


class ChildModel(ndb.Model):
    field_a = ndb.StringProperty()
    field_b = ndb.StringProperty()


class ParentModel(ndb.Model):
    child = ndb.StructuredProperty(ChildModel)


class RepeatedParentModel(ndb.Model):
    children = ndb.StructuredProperty(ChildModel, repeated=True)


class StructuredTestCase(NDBTestCase):
    def test_create_form(self):
        FormCls = model_form(ParentModel)
        form = FormCls()
        self.assertIsInstance(form.child, wtforms.FormField)

        sub_form = form.child.form
        self.assertIsInstance(sub_form.field_a, wtforms.StringField)
        self.assertIsInstance(sub_form.field_b, wtforms.StringField)


class RepeatedStructuredTestCase(NDBTestCase):
    def test_create_form(self):
        FormCls = model_form(RepeatedParentModel)
        form = FormCls()
        self.assertIsInstance(form.children, wtforms.FieldList)

        f = form.children.append_entry()
        self.assertIsInstance(f, wtforms.FormField)

