from zope.interface import Interface, alsoProvides
from zope.app.content import interfaces as contentifaces


class IDatasetEnhanced(Interface):
    """ Marker interface for datasets.
    """

alsoProvides(IDatasetEnhanced, contentifaces.IContentType)
class IDataset(Interface):
    """ Objects which have dataset information.
    """

    def formatTempCoverage(obj):
        """ Return formated temporary coverage for display
        """

class IOrganisation(Interface):
    """ Objects which have organisation information.
    """
