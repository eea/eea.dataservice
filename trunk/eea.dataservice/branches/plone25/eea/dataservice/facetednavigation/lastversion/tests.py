""" Doc tests
"""
import doctest
import unittest
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite
from eea.dataservice.tests.base import DataserviceFunctionalTestCase

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def test_suite():
    """ Suite
    """
    return unittest.TestSuite((
            Suite('facetednavigation/lastversion/widget.txt',
                  optionflags=OPTIONFLAGS,
                  package='eea.dataservice',
                  test_class=DataserviceFunctionalTestCase) ,
              ))
