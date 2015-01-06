"""Autorelations for eea.dataservice"""

# from zope.component import getMultiAdapter


class LatestAssessments(object):
    """ Return the latest assessment for a Data.
    """
    def __init__(self, context):
        """Constructor"""
        self.context = context
        self.request = getattr(self.context, 'REQUEST', None)

    def find_assessments(self, categ, assessments):
        """
        :param categ:
        :type categ:
        :param assessments:
        :type assessments:
        :return:
        :rtype:
        """
        for obj in categ[1]:
            if obj.portal_type in ['DavizVisualization', 'EEAFigure']:
                objrview = obj.unrestrictedTraverse('@@eea.relations.macro')
                ofrels = objrview.forward()
                obwrels = objrview.backward()
                for ocateg in ofrels:
                    for obj in ocateg[1]:
                        if obj.portal_type == "Assessment":
                            assessments.append(obj)
                for ocateg in obwrels:
                    for obj in ocateg[1]:
                        if obj.portal_type == "Assessment":
                            assessments.append(obj)

    def __call__(self, **kwargs):
        """ Return all the related data sets from the assessments figures.
        """
        rview = self.context.unrestrictedTraverse('@@eea.relations.macro')
        fwrels = rview.forward()
        bwrels = rview.backward()
        assessments = []
        for categ in fwrels:
            self.find_assessments(categ, assessments)
        for categ in bwrels:
            self.find_assessments(categ, assessments)
        if assessments:
            return [('Produced Indicators', assessments)]
        return {}
