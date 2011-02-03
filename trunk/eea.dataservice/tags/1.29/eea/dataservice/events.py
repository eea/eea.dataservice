""" New events
"""

from Acquisition import aq_inner, aq_parent
from Products.EEAContentTypes.interfaces import IRelations
from zope.app.event.interfaces import IObjectEvent
from zope.interface import Attribute
from zope.interface import implements


class IFileUploadedEvent(IObjectEvent):
    """ Objects file uploaded
    """
    object = Attribute("The subject of the event.")
    value = Attribute("File value.")

class FileUploadedEvent(object):
    """ Sent if file was changed """
    implements(IFileUploadedEvent)

    def __init__(self, context, value):
        self.object = context
        self.value = value


def handle_eeafigure_state_change(figure, event):
    """Handler for EEAFigure workflow state change"""

    #reindex all Assessments and IndicatorFactSheets that point to this figure
    
    backreferences = IRelations(figure).backReferences()
    assessments = [aq_parent(aq_inner(a)) for a in backreferences 
                                          if a.meta_type == "AssessmentPart"]
    ifs = filter(lambda o:o.meta_type=="IndicatorFactSheet", backreferences)

    for obj in assessments + ifs:
        obj.reindexObject()

