""" User feedback interfaces
"""
from zope.interface import Interface
from zope import schema

class ISurveySupport(Interface):
    """ Survey support
    """
    enabled = schema.Bool(u'Can enable EEAUserFeedback', readonly=True)
    disabled = schema.Bool(u'Can disable EEAUserFeedback', readonly=True)

class ISurvey(Interface):
    """ Survey enable/disable
    """
    def enable():
        """ Enable EEAUserFeedback
        """

    def disable():
        """Disable EEAUserFeedback
        """

class ISurveyView(Interface):
    """ Survey page
    """
