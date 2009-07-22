""" Version widget
"""
from DateTime import DateTime

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from eea.facetednavigation.widgets.widget import Widget as AbstractWidget

class Widget(AbstractWidget):
    """ Widget
    """
    # Widget properties
    widget_type = 'lastversion'
    widget_label = 'Show last version'
    view_js = '++resource++eea.dataservice.facetednavigation.dataservice.view.js'
    edit_js = '++resource++eea.dataservice.facetednavigation.dataservice.edit.js'
    view_css = '++resource++eea.dataservice.facetednavigation.dataservice.view.css'
    edit_css = '++resource++eea.dataservice.facetednavigation.dataservice.edit.css'

    index = ViewPageTemplateFile('widget.pt')
    edit_schema = AbstractWidget.edit_schema

    def after_query(self, brains, form):
        """ Filter brains
        """
        last_versions = {}
        brains = [brain for brain in brains]
        for brain in brains:
            ptype = getattr(brain, 'portal_type', None)
            version_id = getattr(brain, 'getVersionId', '')
            if ptype == 'Data' and len(version_id):
                effective_date = getattr(brain, 'EffectiveDate', DateTime(1970))
                if len(version_id):
                    if last_versions.has_key(version_id):
                        current_date = getattr(last_versions[version_id], 'EffectiveDate', DateTime(1970))
                        if current_date < effective_date:
                            last_versions[version_id] = brain
                    else:
                        last_versions[version_id] = brain

        versions = [k.data_record_id_ for k in last_versions.values()]
        for brain in brains:
            version_id = getattr(brain, 'getVersionId', '')
            if ptype == 'Data' and len(version_id):
                if brain.data_record_id_ in versions:
                    yield brain
            else:
                yield brain
