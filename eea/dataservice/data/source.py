""" figure multi data provenance
"""
from zope.interface import implementer

from eea.app.visualization.interfaces import IMultiDataProvenance
from eea.app.visualization.data.source import MultiDataProvenance

@implementer(IMultiDataProvenance)
class EEAFigureMultiDataProvenance(MultiDataProvenance):
    """ eea figure multi data provenance from relations
    """
