from __future__ import unicode_literals
import decimal

from wtforms import fields

from .ndb import *


class GeoPtPropertyField(fields.StringField):

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                lat, lon = valuelist[0].split(',')
                self.data = '%s,%s' % (
                    decimal.Decimal(lat.strip()),
                    decimal.Decimal(lon.strip()),)

            except (decimal.InvalidOperation, ValueError):
                raise ValueError('Not a valid coordinate location')
