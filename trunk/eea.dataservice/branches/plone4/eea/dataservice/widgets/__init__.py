""" Custom AT widgets
"""
from Products.Archetypes.Registry import registerWidget
from eea.dataservice.widgets.FigureTypeWidget import FigureTypeWidget
from eea.dataservice.widgets.GeoQualityWidget import GeoQualityWidget

def register():
    """ Custom AT registrations
    """
    registerWidget(FigureTypeWidget,
        title='EEA Fugure Type',
        description=('EEA Figure Type description.'),
        used_for=('Products.Archetypes.Field.StringField',
                  'Products.Archetypes.Field.LinesField',))

    registerWidget(GeoQualityWidget,
        title='Geographic information quality',
        description=('Geographic information quality label.'),
        used_for=('eea.dataservice.fields.GeoQualityField.GeoQualityField'))
