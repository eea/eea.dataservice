""" Custom AT widgets
"""
from Products.Archetypes.Registry import registerWidget
from eea.dataservice.widgets.FigureTypeWidget import FigureTypeWidget
from eea.dataservice.widgets.organisations import OrganisationsWidget
from eea.dataservice.widgets.organisations import MultiOrganisationsWidget

def register():
    """ Custom AT registrations
    """
    registerWidget(FigureTypeWidget,
        title='EEA Figure Type',
        description=('EEA Figure Type description.'),
        used_for=('Products.Archetypes.Field.StringField',
                  'Products.Archetypes.Field.LinesField',))

    registerWidget(OrganisationsWidget,
        title='EEA Organisations',
        description='EEA Organisations description',
        user_for=('Products.Archetypes.Field.StringField',))

    registerWidget(MultiOrganisationsWidget,
            title='EEA Multiple Organisations',
            description='EEA Multiple Organisations description',
            user_for=('Products.Archetypes.Field.LinesField',))
