""" Doc tests
"""
import doctest
import unittest
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite
from eea.dataservice.tests.base import DataserviceFunctionalTestCase

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
    suite = ()

    if FACETED:
        suite += (
            Suite('facetednavigation/lastversion/widget.txt',
                  optionflags=OPTIONFLAGS,
                  package='eea.dataservice',
                  test_class=DataserviceFunctionalTestCase) ,
        )

    return unittest.TestSuite(suite)
