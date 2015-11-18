""" Organisation
"""

from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.Field import decode  # , encode
from Products.Archetypes.atapi import StringField  # ,ObjectField


class OrganisationField(StringField):
    """ Organisation Field
    """

    def set(self, instance, value, **kwargs):
        """ Setter
        """

        fname = self.getName()

        if not getattr(self, 'raw', False):  # Remove acquisition wrappers
            value = decode(aq_base(value), instance, **kwargs)

        new_value = value
        try:
            old_value = self.getStorage(instance).get(fname, instance)
        except AttributeError:
            old_value = None

        # make changes only if new value is different from old value
        if new_value != old_value:
            kwargs['field'] = self
            self.getStorage(instance).set(self.getName(), instance, new_value,
                                          **kwargs)

            if not old_value:
                return

            # ZZZ: doing this in field set code is weird, should
            # have been done by definining a new event
            # this would have avoided hardcoding field here

            # Update organisation URL to depedencies
            fields = {'dataOwner': 'getDataOwner',
                      'processor': 'getProcessor'}

            cat = getToolByName(instance, 'portal_catalog')

            for fieldname, index in fields.items():
                for b in cat.searchResults({index: old_value}):
                    obj = b.getObject()

                    field = obj.getField(fieldname)
                    if not field:
                        continue

                    val = [new_value]  # we're dealing with LinesField fields

                    fvalue = field.getAccessor(obj)()
                    if isinstance(fvalue, (list, tuple)):
                        val = list(set(val + list(fvalue)))

                    mutator = field.getMutator(obj)
                    mutator(val)

                    obj.reindexObject()
