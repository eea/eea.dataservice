""" Workflow scripts
"""
from zope.component import queryMultiAdapter

def sendWorkflowEmail(self, state_change, **kw):
    """ Send email
    """
    obj = getattr(state_change, 'object', None)
    request = getattr(obj, 'REQUEST', None)
    wfsupport = queryMultiAdapter((obj, request), name=u'eea-workflow-support')
    if wfsupport:
        wf = wfsupport(state_change, None)
        subject = wf.subject or '[EEA CMS] - workflow changed for %s'
        return wf.sendEmail(subject)
