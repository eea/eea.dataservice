"""Autorelations for eea.dataservice"""

from Products.CMFCore.utils import getToolByName


class LatestAssessments(object):
    """ Return the latest assessment for a Data.
    """
    def __init__(self, context):
        """Constructor"""
        self.context = context
        self.request = getattr(self.context, 'REQUEST', None)
        self.wftool = getToolByName(context, 'portal_workflow')

    def related_assessments(self, relation, is_anon=False):
        """
        :param relation: Tuple ('relation_name', ['relation']
        :type relation: tuple
        :param is_anon: Boolean indicating whether we have an anon user
        :type is_anon: bool
        :return: List of related Assessments
        :rtype: list
        """
        alist = []
        for obj in relation[1]:
            if obj.portal_type in ['DavizVisualization', 'EEAFigure']:
                objrview = obj.unrestrictedTraverse('@@eea.relations.macro')
                obwrels = objrview.backward()
                for backrel in obwrels:
                    for back_obj in backrel[1]:
                        if back_obj.portal_type in ["Assessment",
                                                    "AssessmentPart"]:
                            if is_anon:
                                state = self.wftool.getInfoFor(back_obj,
                                                          'review_state', '')
                                if state == "published":
                                    alist.append(back_obj)
                            else:
                                alist.append(back_obj)
        return alist

    def __call__(self, **kwargs):
        """ Return all the related data sets from the assessments figures.
        """
        rview = self.context.unrestrictedTraverse('@@eea.relations.macro')
        fwrels = rview.forward()
        bwrels = rview.backward()
        assessments = []
        is_anon = self.is_anon_user()
        for relation in fwrels:
            assessments.extend(self.related_assessments(relation,
                                                        is_anon=is_anon))
        for relation in bwrels:
            assessments.extend(self.related_assessments(relation,
                                                        is_anon=is_anon))
        if assessments:
            return [('Produced Indicators', assessments)]
        return {}

    def is_anon_user(self):
        """
        :return: Boolean indicating if visitor is an anonymous user or not
        :rtype: bool
        """
        mtool = getToolByName(self.context, 'portal_membership')
        return bool(mtool.isAnonymousUser())
