""" Backward compatible
"""
from eea.versions.interfaces import IVersionControl
from eea.versions.interfaces import IVersionEnhanced
from eea.versions.interfaces import IGetVersions

__all__ = [
    IVersionControl.__name__,
    IVersionEnhanced.__name__,
    IGetVersions.__name__,
]

from Products.CMFPlone.log import log_deprecated
log_deprecated("eea.dataservice.versions.interfaces is deprecated and it "
               " will be removed in eea.dataservice > 4.0 "
               "Please use eea.versions.interfaces instead.")
