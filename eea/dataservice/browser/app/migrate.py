from Products.Five import BrowserView

EXTCONTAINER = '/www/SITE/data-and-maps/data/external'

class MigrateDatasetsToExternalDatasets(BrowserView):
    """ Migrate an Data object to a ExternalDataSpec
    """

    def __call__(self):
        eds_id = self.context.getId()
        extcontainer = self.context.unrestrictedTraverse(EXTCONTAINER)
        data_ob = self.context

        # Create new ExternalDataSpec object
        eds_id = extcontainer.invokeFactory('ExternalDataSpec', id=eds_id)
        eds_ob = getattr(extcontainer, eds_id)

        # Mapping metadata
        eds_ob.setTitle(data_ob.Title())
        eds_ob.setDescription(data_ob.Description())
        eds_ob.setEffectiveDate(data_ob.getEffectiveDate())
        eds_ob.setCreationDate(data_ob.creation_date)
        eds_ob.setSubject(data_ob.Subject())
        eds_ob.setCreators(data_ob.Creators())


        #TODO: Data -> ExternalDataSpec mapping
        #TODO: relatedItems

        eds_ob.reindexObject()

        #TODO: delete or change state to old Data object?
        #TODO: fix redirect
        return 'Migration done.'
