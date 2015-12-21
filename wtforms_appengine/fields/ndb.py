from __future__ import unicode_literals

import json
import operator

from wtforms import fields, widgets
# from wtforms.compat import text_type, string_types

__all__ = [
    'KeyPropertyField',
    'JsonPropertyField']


class KeyPropertyField(fields.SelectFieldBase):
    """
    A field for ``ndb.KeyProperty``. The list items are rendered in a select.

    :param reference_class:
        A db.Model class which will be used to generate the default query
        to make the list of items. If this is not specified, The `query`
        property must be overridden before validation.
    :param get_label:
        If a string, use this attribute on the model class as the label
        associated with each option. If a one-argument callable, this callable
        will be passed model instance and expected to return the label text.
        Otherwise, the model object's `__str__` or `__unicode__` will be used.
    :param allow_blank:
        If set to true, a blank choice will be added to the top of the list
        to allow `None` to be chosen.
    :param blank_text:
        Use this to override the default blank option's label.
    """
    widget = widgets.Select()

    def __init__(self, label=None, validators=None, reference_class=None,
                 get_label=None, allow_blank=False, blank_text='', **kwargs):
        super(KeyPropertyField, self).__init__(label, validators, **kwargs)
        if get_label is None:
            self.get_label = lambda x: x
        elif isinstance(get_label, basestring):
            self.get_label = operator.attrgetter(get_label)
        else:
            self.get_label = get_label

        self.allow_blank = allow_blank
        self.blank_text = blank_text
        self._set_data(None)
        if reference_class is not None:
            self.query = reference_class.query()

    def _get_data(self):
        if self._formdata is not None:
            for obj in self.query:
                if str(obj.key.id()) == self._formdata:
                    self._set_data(obj.key)
                    break
        return self._data

    def _set_data(self, data):
        self._data = data
        self._formdata = None

    data = property(_get_data, _set_data)

    def iter_choices(self):
        if self.allow_blank:
            yield ('__None', self.blank_text, self.data is None)

        for obj in self.query:
            key = str(obj.key.id())
            label = self.get_label(obj)
            yield (key, label, (self.data == obj.key) if self.data else False)

    def process_formdata(self, valuelist):
        if valuelist:
            if valuelist[0] == '__None':
                self.data = None
            else:
                self._data = None
                self._formdata = valuelist[0]

    def pre_validate(self, form):
        if self.data is not None:
            for obj in self.query:
                if self.data == obj.key:
                    break
            else:
                raise ValueError(self.gettext('Not a valid choice'))
        elif not self.allow_blank:
            raise ValueError(self.gettext('Not a valid choice'))


class JsonPropertyField(fields.StringField):
    """
    This field is the base for most of the more complicated fields, and
    represents an ``<input type="text">``.
    """
    widget = widgets.TextArea()

    def process_formdata(self, valuelist):
        if valuelist is not "":
            self.data = json.loads(valuelist[0])
        else:
            self.data = None

    def _value(self):
        return json.dumps(self.data) if self.data is not None else ''


