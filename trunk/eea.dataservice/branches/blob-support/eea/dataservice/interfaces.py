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

    def getOrganisationName(obj):
        """ Return organisation name
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

class IEEAFigure(Interface):
    """ Marker interface for EEAFigure.
    """

class IEEAFigureMap(Interface):
    """ Marker interface for Map
    """

class IEEAFigureGraph(Interface):
    """ Marker interface for Graph
    """

class IEEAFigureTable(Interface):
    """ Marker interface for Table
    """

class IEEAFigureFile(Interface):
    """ Marker interface for Figure File
    """

class IImageFS(Interface):
    """ Marker interface for Image Filesystem
    """

class IWorkingList(Interface):
    """ Marker interface for ATTopic
    """