""" New events
"""
from zope.component import queryAdapter
from Acquisition import aq_inner, aq_parent
from eea.dataservice.relations import IRelations
from eea.dataservice.interfaces import IDataset, IDatatable
from Products.CMFPlone import utils

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

def reindex_filetype(obj, event):
    """ Reindex datatable and dataset parents filetype index onn DataFile change
    """
    parent = utils.parent(obj)
    if IDatatable.providedBy(parent):
        parent.reindexObject(idxs=['filetype'])

    parent = utils.parent(parent)
    if IDataset.providedBy(parent):
        parent.reindexObject(idxs=['filetype'])
