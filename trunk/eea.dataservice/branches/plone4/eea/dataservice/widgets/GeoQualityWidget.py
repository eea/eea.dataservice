""" Geo quality
"""
from Products.Archetypes.Widget import TypesWidget

class GeoQualityWidget(TypesWidget):
    """ Geo Quality Widget
    """
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'format': "flex", # possible values: flex, select, radio
        'macro' : "quality_widget",
        'helper_js': ('quality_widget.js',),
        })

    def process_form(self, instance, field, form, empty_marker='',
                     emptyReturnsMarker=False, validating=True):
        """ Process form """
        name = field.getName()
        gq_completeness = form.get('%sCom' % name, None)
        gq_logical = form.get('%sLog' % name, None)
        gq_position = form.get('%sPos' % name, None)
        gq_temporal = form.get('%sTem' % name, None)
        gq_thematic = form.get('%sThe' % name, None)

        if not (gq_completeness or gq_logical or
                gq_position or gq_temporal or gq_thematic):
            return empty_marker

        return (gq_completeness, gq_logical, gq_position,
                gq_temporal, gq_thematic), {}
