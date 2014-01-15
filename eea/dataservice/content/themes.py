""" Safely import themes
"""
try:
    from eea.themecentre.content import ThemeTaggable
    ThemeTaggable = ThemeTaggable.ThemeTaggable
except ImportError:
    class ThemeTaggable(object):
        """ Empty
        """

try:
    from eea.themecentre import interfaces
    IThemeTagging = interfaces.IThemeTagging
except ImportError:
    from zope.interface import Interface
    class IThemeTagging(Interface):
        """ Theme tagging interface
        """
