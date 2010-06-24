""" Doc tests
"""
import doctest
import unittest
from base import DataserviceFunctionalTestCase
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


def test_suite():
    """ Suite
    """
    return unittest.TestSuite((
            Suite('doc/datasets.txt',
                  optionflags=OPTIONFLAGS,
                  package='eea.dataservice',
                  test_class=DataserviceFunctionalTestCase) ,
            Suite('doc/catalog.txt',
                  optionflags=OPTIONFLAGS,
                  package='eea.dataservice',
                  test_class=DataserviceFunctionalTestCase) ,
            Suite('doc/figures.txt',
                  optionflags=OPTIONFLAGS,
                  package='eea.dataservice',
                  test_class=DataserviceFunctionalTestCase) ,
            Suite('doc/figure_file.txt',
                  optionflags=OPTIONFLAGS,
                  package='eea.dataservice',
                  test_class=DataserviceFunctionalTestCase) ,
              ))
