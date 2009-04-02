from zope.interface import Interface, alsoProvides
from zope.app.content import interfaces as contentifaces


class IDatasetEnhanced(Interface):
    """ Marker interface for datasets.
    """

alsoProvides(IDatasetEnhanced, contentifaces.IContentType)
class IDataset(Interface):
    """ Objects which have dataset information.
    """

    def getKeywords(obj):
        """ Return formated keywords list
        """

    def formatTempCoverage(obj):
        """ Return formated temporary coverage for display
        """

class IDatafile(Interface):
    """ Objects which have dataset file information.
    """

class IDatatable(Interface):
    """ Objects which have dataset table information.
    """

class IDatasubtable(Interface):
    """ Objects which have dataset sub-table information.
    """

class IOrganisation(Interface):
    """ Objects which have organisation information.
    """

    def getDataRows(obj):
        """ Return datasets which are owned by this organisation
        """
