""" Doc tests
"""
import doctest
import logging
import unittest

try:
    import eea.rdfmarshaller as has_marshaller
except ImportError:
    has_marshaller = False
    logger = logging.getLogger("eea.dataservice")
    logger.warning("Could not find eea.rdfmarshaller package")

from eea.dataservice.tests.base import FUNCTIONAL_TESTING
from plone.testing import layered



OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)



def test_suite():
    """ Suite
    """
    suite = unittest.TestSuite()

    if has_marshaller:
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
