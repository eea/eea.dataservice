""" Migrate
"""
import logging
from zope.component import queryAdapter
from zope.component import getMultiAdapter
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from eea.dataservice.relations import IRelations

# Logging
logger = logging.getLogger('eea.indicators')
info = logger.info
info_exception = logger.exception

EXTCONTAINER = '/www/SITE/data-and-maps/data/external'

class MigrateDatasetsToExternalDatasets(BrowserView):
    """ Migrate an Data object to a ExternalDataSpec
    """

    def __call__(self):
        eds_id = self.context.getId()
        extcontainer = self.context.unrestrictedTraverse(EXTCONTAINER)
        data_ob = self.context
        request = self.request
        msg = ''
        err_msg = ''

        # Create new ExternalDataSpec object
        try:
            eds_id = extcontainer.invokeFactory('ExternalDataSpec', id=eds_id)
            eds_ob = getattr(extcontainer, eds_id)

            # Mapping metadata
            eds_ob.setTitle(data_ob.Title())
            eds_ob.setDescription(data_ob.Description())
            eds_ob.setEffectiveDate(data_ob.getEffectiveDate())
            eds_ob.setCreationDate(data_ob.creation_date)
            eds_ob.setSubject(data_ob.Subject())
            eds_ob.setCreators(data_ob.Creators())

            owner = data_ob.getDataOwner()
            if owner:
                eds_ob.setProvider_url(owner[0])
                if len(owner) > 1:
                    msg += 'Warning, there were more then one owner.'

            temporal = data_ob.getTemporalCoverage()
            if temporal:
                FormatTempCoverage = getMultiAdapter((data_ob, request),
                                                     name=u'formatTempCoverage')
                eds_ob.setTimeliness(FormatTempCoverage())

            eds_ob.setOther_comments(data_ob.getMoreInfo())
            eds_ob.setCategory_of_use('DataUseCategory_04')

            # Map relatedItems. All forward and backward references of the
            # data object are removed
            forwards = data_ob.getRelatedItems()

            backs = []
            relations = queryAdapter(data_ob, IRelations)
            if relations:
                backs = relations.backReferences()

            if forwards:
                eds_ob.setRelatedItems(forwards)
                data_ob.setRelatedItems([])

            for ob in backs:
                related = ob.getRelatedItems()
                del related[related.index(data_ob)]
                related.append(eds_ob)
                ob.setRelatedItems(related)

            forwards = data_ob.getRelatedProducts()
            if relations:
                backs = relations.backReferences(relatesTo='relatesToProducts')

            if forwards:
                eds_ob.setRelatedItems(forwards)
                data_ob.setRelatedProducts([])

            for ob in backs:
                related = ob.getRelatedProducts()
                del related[related.index(data_ob)]
                related.append(eds_ob)
                ob.setRelatedProducts(related)

            # Migrate DataSource
            datasource = data_ob.getDataSource()

            tables = data_ob.objectValues('DataTable')
            for table in tables:
                for datafile in table.objectValues('DataFile'):
                    if datafile.content_type == 'text/plain':
                        datasource += '<br />'
                        datasource += datafile.getFile().data

            eds_ob.setDataset_path(datasource)

            # Change data object state to 'draft'
            wftool = getToolByName(data_ob, 'portal_workflow')
            state = wftool.getInfoFor(data_ob, 'review_state')
            wf_msg = 'Set by migrate Data to ExternalDataSpec action.'

            if state in ['published', 'published_eionet', 'visible']:
                wftool.doActionFor(data_ob, 'retract', comment=wf_msg)
                wftool.doActionFor(data_ob, 'enable', comment=wf_msg)
            elif state in ['retracted']:
                wftool.doActionFor(data_ob, 'enable', comment=wf_msg)
            elif state in ['content_pending']:
                wftool.doActionFor(data_ob, 'reject', comment=wf_msg)
            elif state in ['draft']:
                pass
            else:
                info('WARNING: Unknown state')
            msg += 'Original data object was set to state: draft.'

            eds_ob.reindexObject()
        except Exception, err:
            info('ERROR: on migrating Data to ExternalDataSpec')
            info_exception('Exception: %s ', err)
            err_msg = 'Error creating ExternalDataSpec, please check zope log.'


        if err_msg:
            IStatusMessage(request).addStatusMessage(err_msg, type='info')
            request.response.redirect(data_ob.absolute_url())
        else:
            IStatusMessage(request).addStatusMessage(msg, type='info')
            request.response.redirect(eds_ob.absolute_url())
