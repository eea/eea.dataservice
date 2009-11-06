from zope.interface import Interface, Attribute

class IVersionControl(Interface):
    """ Objects which have versions.
    """
    versionId = Attribute("Version ID")

    def getVersionNumber():
        """ Return version number. """

class IVersionEnhanced(Interface):
    """ Objects which have versions.
    """

class IGetVersions(Interface):
    """ Get container versions
    """
    def newest():
        """ Return newer versions
        """

    def oldest():
        """ Return oldest versions
        """

    def __call__():
        """ Get all versions
        """
