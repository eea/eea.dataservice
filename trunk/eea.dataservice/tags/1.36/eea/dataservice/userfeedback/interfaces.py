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
    def enable(): #pylint: disable-msg = E0211
        """ Enable EEAUserFeedback
        """

    def disable(): #pylint: disable-msg = E0211
        """Disable EEAUserFeedback
        """

class ISurveyView(Interface):
    """ Survey page
    """
