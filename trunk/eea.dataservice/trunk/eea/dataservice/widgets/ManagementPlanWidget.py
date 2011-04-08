# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget
from zope.app.form.browser.interfaces import IBrowserWidget
from zope.app.form.interfaces import IInputWidget
from zope.app.form.interfaces import WidgetInputError
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.interface import implements
from zope.schema import Field
from zope.schema.interfaces import IField
from zope.app.form.browser.interfaces import IWidgetInputErrorView
from zope.component import getMultiAdapter
from zope.schema.vocabulary import getVocabularyRegistry


class ManagementPlanWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'format': "flex", # possible values: flex, select, radio
        'macro' : "management_plan_widget",
        })

    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker='',
                     emptyReturnsMarker=False, validating=True):
        """ process form """
        name = field.getName()
        mp_year = form.get('%sYear' % name, None)
        mp_code = form.get('%sCode' % name, None)

        if mp_year is None or mp_code is None:
            return empty_marker

        return (mp_year, mp_code), {}

registerWidget(ManagementPlanWidget,
               title='EEA Management Plan Code',
               description=('Renders a HTML selection widget, to'
                            ' allow you enter the year and the'
                            ' EEA management plan code'),
               used_for=('eea.dataservice.fields.ManagementPlanField.ManagementPlanField')
               )


class IManagementPlanCode(IField):
    """The management plan field interface"""


class ManagementPlanCode(Field):
    """The management plan field"""

    implements(IManagementPlanCode)

    years_vocabulary = None

    _type = (tuple, list)
    
    def __init__(self, *args, **kwds):
        self.years_vocabulary = kwds['years_vocabulary']
        del kwds['years_vocabulary']
        Field.__init__(self, *args, **kwds)

    def get(self, adapter):
        value = getattr(adapter, self.__name__, ())
        return value

    def set(self, adapter, value):
        if self.readonly:
            raise TypeError("Can't set values on read-only fields "
                            "(name=%s, class=%s.%s)"
                            % (self.__name__,
                               object.__class__.__module__,
                               object.__class__.__name__))

        setattr(adapter, self.__name__, value)

    def constraint(self, value):

        if not self.required:
            return True
        if len(value) != 2:
            return False

        if not isinstance(value, self._type):
            return False

        vocab = self.getVocabulary()
        year, code = value

        try:
            int(year)
        except ValueError:
            return False

        if year:
            try:
                term = vocab.getTermByToken(year)
            except KeyError:
                return False

        if code:
            code = code.strip()

        if not len(code) > 0:
            return False

        return True

    def getVocabulary(self):
        vocab = self.years_vocabulary
        context = self.context.context
        return getVocabularyRegistry().get(context, vocab)


class FormlibManagementPlanWidget(object):
    implements(IBrowserWidget, IInputWidget)
    template = ViewPageTemplateFile("managementplan.pt")

    # See zope.app.form.interfaces.IInputWidget
    name = None
    label = property(lambda self: self.context.title)
    hint = property(lambda self: self.context.description)
    visible = True
    required = property(lambda self: self.context.required)

    _prefix = "form."
    _value = None
    _error = None

    def __init__(self, field, request):
        self.context = field
        self.request = request
        self.name = self._prefix + field.__name__

        self._value = field.query(field.context)

    def applyChanges(self, content):
        """See zope.app.form.interfaces.IInputWidget"""
        field = self.context
        new_value = self.getInputValue()
        old_value = field.query(content, self)
        # The selection has not changed
        if new_value == old_value:
            return False
        field.set(content, new_value)
        return True

    def setPrefix(self, prefix):
        """See zope.app.form.interfaces.IWidget"""
        # Set the prefix locally
        if not prefix.endswith("."):
            prefix += '.'
        self._prefix = prefix
        self.name = prefix + self.context.__name__

    def setRenderedValue(self, value):
        """See zope.app.form.interfaces.IWidget"""
        self._value = value

    def getInputValue(self):
        """See zope.app.form.interfaces.IInputWidget"""
        self._error = None

        year = self.request.form.get(self.name + "Year")
        code = self.request.form.get(self.name + "Code")

        if not self.hasValidInput():
            self._error = WidgetInputError(self.context.__name__, 
                                           self.label, (year, code))
            raise self._error

        year = int(year.strip())        
        code = code.strip()

        return (year, code)

    def hasInput(self):
        """See zope.app.form.interfaces.IInputWidget"""

        code = self.request.form.get(self.name + "Code", '').strip()
        year = self.request.form.get(self.name + "Year", '').strip()

        return bool(code or year)

    def hasValidInput(self):
        """See zope.app.form.interfaces.IInputWidget"""

        code = self.request.form.get(self.name + "Code")
        year = self.request.form.get(self.name + "Year")

        return self.context.constraint((year, code))

    def hidden(self):
        """See zope.app.form.browser.interfaces.IBrowserWidget"""
        return False

    def error(self):
        """See zope.app.form.browser.interfaces.IBrowserWidget"""
        if self._error:
            return "Need valid input"

        #getMultiAdapter((self._error, self.request), 
        #                IWidgetInputErrorView).snippet()

    def __call__(self):
        return self.template()

