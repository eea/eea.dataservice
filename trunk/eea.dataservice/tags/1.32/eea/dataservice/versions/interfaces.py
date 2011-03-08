from eea.versions.interfaces import (
    IVersionControl,
    IVersionEnhanced,
    IGetVersions
)

class IVersionControl(IVersionControl):
    """ Objects which have versions.
    """

class IVersionEnhanced(IVersionEnhanced):
    """ Objects which have versions.
    """

class IGetVersions(IGetVersions):
    """ Get container versions.
    """
