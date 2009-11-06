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