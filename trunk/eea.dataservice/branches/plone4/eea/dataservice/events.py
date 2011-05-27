""" New events
"""
from zope.component import queryAdapter
from Acquisition import aq_inner, aq_parent
from eea.dataservice.relations import IRelations
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


    adapter = queryAdapter(figure, IRelations)
    if not adapter:
        return

    backreferences = adapter.backReferences()
    assessments = [aq_parent(aq_inner(a)) for a in backreferences
                                          if a.meta_type == "AssessmentPart"]
    #ifs = filter(lambda o:o.meta_type=="IndicatorFactSheet", backreferences)
    ifs = [o for o in backreferences if o.meta_type=="IndicatorFactSheet"]

    for obj in assessments + ifs:
        obj.reindexObject()

