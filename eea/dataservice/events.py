""" New events
"""

from Acquisition import aq_inner, aq_parent
from Products.CMFPlone import utils
from Products.statusmessages.interfaces import IStatusMessage
from eea.dataservice.converter.converter import task_convert_figure
from eea.dataservice.interfaces import IDataset, IDatatable
from eea.dataservice.relations import IRelations
from plone.app.async.interfaces import IAsyncService
from zope.component import queryAdapter, getUtility
from Products.CMFCore.utils import getToolByName

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

def handle_eeafigurefile_modified(obj, event):
    """Handles creation or editing of EEAFigureFile

    Creates a new plone.app.async job that converts the file
    """

    if obj.REQUEST.form.get('file_file'):
        async = getUtility(IAsyncService)
        job = async.queueJob(task_convert_figure, obj)
        obj._convertjob = job
        IStatusMessage(obj.REQUEST).add(
                 "Figure will be automatically converted, please "
                 "wait a few minutes", type="INFO")

def handle_eeafigure_versioned(obj, event):
    """Handles versioning of eeafigure
    """
    copy = event.object
    copy.setDataSource("")

def eeafigurefile_local_policy(obj, event):
    """ Setup local workflow policy for Image inside EEAFigureFiles
    """
    ppw = getToolByName(obj, 'portal_placeful_workflow')
    config = ppw.getWorkflowPolicyConfig(obj)
    if not config:
            obj.manage_addProduct['CMFPlacefulWorkflow'].manage_addWorkflowPolicyConfig()
            config = ppw.getWorkflowPolicyConfig(obj)
            config.setPolicyBelow('eeafigurefile_image_workflow', False)
