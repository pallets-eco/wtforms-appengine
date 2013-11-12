WTForms-Appengine
=================
.. module:: wtforms_appengine

WTForms-Appengine includes support for AppEngine fields as well as auto-form
generation from models.

.. note:: 
    WTForms-Appengine supports both `appengine.ext.db` and `appengine.ext.ndb` 
    style models now, and there is some overlap between them. For the near 
    future, we will continue to support both, but at some point will go to 
    only supporting AppEngine for python 2.7 and drop support for ext.db 
    models as well.

Model Forms
-----------
.. automodule:: wtforms_appengine.db


.. autofunction:: model_form(model, base_class=Form, only=None, exclude=None, field_args=None, converter=None)

Datastore-backed Fields
-----------------------
.. module:: wtforms_appengine.fields

.. autoclass:: ReferencePropertyField(default field arguments, reference_class=None, get_label=None, allow_blank=False, blank_text='')

.. autoclass:: StringListPropertyField(default field arguments)

.. autoclass:: IntegerListPropertyField(default field arguments)

.. autoclass:: GeoPtPropertyField(default field arguments)

NDB
---

WTForms now includes support for NDB models and can support mapping the 
relationship fields as well as generating forms from models.

.. autoclass:: KeyPropertyField(default field arguments, reference_class=None, get_label=None, allow_blank=False, blank_text='')

.. module:: wtforms_appengine.ndb

.. autofunction:: model_form(model, base_class=Form, only=None, exclude=None, field_args=None, converter=None)


