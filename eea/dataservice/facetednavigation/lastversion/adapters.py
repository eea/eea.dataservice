""" Adapters
"""
import logging
from zope.interface import implements
from eea.facetednavigation.interfaces import IWidgetFilterBrains
logger = logging.getLogger('faceted_lastest_version')


class WidgetFilterBrains(object):
    """ Filter brains after query
    """
    implements(IWidgetFilterBrains)

    def __init__(self, context):
        self.widget = context

    def __call__(self, brains, form):
        """ Filter brains
        """
        #
        # WARNING: DO NOT touch this code, otherwise I'll use `git blame`
        #
        # Every time you do, you introduce new bugs and performance regression,
        # and I'll have to fix it.
        #
        # It works as expected, trust me.
        #
        # It is supposed to filter the given brains NOT to
        # add new ones. Thus, it extracts latest versions from the given set
        # of brains even if some are not the latest versions of the objects.
        #
        # If the latest version doesn't match the search criteria, then
        # it is a content inconsistency issue and the content should be fixed,
        # not the code.
        #
        # You CAN'T search for `water` and get `air` related results. You
        # will get the latest version that is about 'water'.
        #
        # Ticket: #83219
        #
        latest = {}
        for brain in brains:
            vid = getattr(brain, 'getVersionId', '')

            # #17812 the brain can be a discussion object which
            # returns Missing.Value when retrieving the getVersionId
            if not vid:
                continue

            if not isinstance(vid, basestring):
                logger.warn('%s has a wrong version_id: %s',
                    brain.getURL(), vid)

            if vid not in latest:
                latest[vid] = brain
                continue

            brain_date = max(
                brain.effective.asdatetime(),
                brain.created.asdatetime()
            )

            last = latest[vid]
            last_date = max(
                last.effective.asdatetime(),
                last.created.asdatetime()
            )

            if last_date < brain_date:
                latest[vid] = brain

        rids = set(brain.getRID() for brain in latest.values())
        for brain in brains:
            if brain.getRID() not in rids:
                continue
            yield brain
