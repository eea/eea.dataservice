""" Organisations Widgets
"""
from Products.Archetypes.public import MultiSelectionWidget, SelectionWidget

class OrganisationsWidget(SelectionWidget):
    """ One organisation widget
    """
    _properties = SelectionWidget._properties.copy()
    _properties.update({
        'format': "select", # possible values: flex, select, radio
        'macro' : "organisation_widget",
        'helper_js': ("selectautocomplete_widget.js",),
        })

class MultiOrganisationsWidget(MultiSelectionWidget):
    """ Multiple organisations widget
    """
    _properties = MultiSelectionWidget._properties.copy()
    _properties.update({
        'macro' : "organisations_widget",
        'size'  : 15,
        'helper_js': ("multiselectautocomplete_widget.js",),
    })
