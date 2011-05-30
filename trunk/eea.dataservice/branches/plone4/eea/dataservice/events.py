""" New events
"""
from zope.component import queryAdapter
from Acquisition import aq_inner, aq_parent
from eea.dataservice.relations import IRelations

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
    ifs = [o for o in backreferences if o.meta_type == "IndicatorFactSheet"]

    for obj in assessments + ifs:
        obj.reindexObject()

