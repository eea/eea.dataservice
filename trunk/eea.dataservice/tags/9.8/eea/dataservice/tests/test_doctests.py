""" Doc tests
"""
import doctest
import unittest
from eea.dataservice.tests.base import FUNCTIONAL_TESTING
from plone.testing import layered
import logging

logger = logging.getLogger("eea.dataservice")

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

HAS_Marshaller = False
try:
    import eea.rdfmarshaller as HAS_Marshaller
except ImportError:
    logger.warning("Could not find eea.rdfmarshaller package")

def test_suite():
    """ Suite
    """
    suite = unittest.TestSuite()

    if HAS_Marshaller:
        suite.addTests([
            layered(
                doctest.DocFileSuite(
                    'doc/marshaller.txt',
                    optionflags=OPTIONFLAGS,
                    package='eea.dataservice'),
                layer=FUNCTIONAL_TESTING),])

    suite.addTests([
        layered(
            doctest.DocFileSuite(
                'doc/mimetypes.txt',
                optionflags=OPTIONFLAGS,
                package='eea.dataservice'),
            layer=FUNCTIONAL_TESTING),
        layered(
            doctest.DocFileSuite(
                'doc/catalog.txt',
                optionflags=OPTIONFLAGS,
                package='eea.dataservice'),
            layer=FUNCTIONAL_TESTING),
        layered(
            doctest.DocFileSuite(
                'doc/convert_figures.txt',
                optionflags=OPTIONFLAGS,
                package='eea.dataservice'),
            layer=FUNCTIONAL_TESTING),
        layered(
            doctest.DocFileSuite(
                'doc/datasets.txt',
                optionflags=OPTIONFLAGS,
                package='eea.dataservice'),
            layer=FUNCTIONAL_TESTING),
        layered(
            doctest.DocFileSuite(
                'doc/figures.txt',
                optionflags=OPTIONFLAGS,
                package='eea.dataservice'),
            layer=FUNCTIONAL_TESTING),
        layered(
            doctest.DocFileSuite(
                'doc/figure_file.txt',
                optionflags=OPTIONFLAGS,
                package='eea.dataservice'),
            layer=FUNCTIONAL_TESTING),
        layered(
            doctest.DocFileSuite(
                'doc/topdatasets.txt',
                optionflags=OPTIONFLAGS,
                package='eea.dataservice'),
            layer=FUNCTIONAL_TESTING),
        layered(
            doctest.DocFileSuite(
                'doc/topfigures.txt',
                optionflags=OPTIONFLAGS,
                package='eea.dataservice'),
            layer=FUNCTIONAL_TESTING),
    ])
    return suite
