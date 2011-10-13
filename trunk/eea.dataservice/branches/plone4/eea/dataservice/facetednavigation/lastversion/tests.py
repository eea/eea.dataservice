""" Doc tests
"""
import doctest
import unittest
from eea.dataservice.tests.base import FUNCTIONAL_TESTING
from plone.testing import layered

try:
    from eea.facetednavigation import interfaces
    # See http://goo.gl/eHbyY
    FACETED = True if interfaces.IFacetedNavigable else False
except ImportError:
    FACETED = False

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def test_suite():
    """ Suite
    """
    suite = unittest.TestSuite()

    if FACETED:
        suite.addTests([
            layered(
                doctest.DocFileSuite(
                    'facetednavigation/lastversion/widget.txt',
                    optionflags=OPTIONFLAGS,
                    package='eea.dataservice'),
                layer=FUNCTIONAL_TESTING),
        ])

    return suite
