""" Geographical coverage widget
"""
import logging
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from BTrees.IIBTree import weightedIntersection, IISet
from eea.facetednavigation.widgets.checkbox.widget import Widget as CWidget
from eea.dataservice.facetednavigation.geocoverage.interfaces import (
  DefaultSchemata,
  LayoutSchemata,
  DisplaySchemata,
  CountableSchemata,
)


logger = logging.getLogger('eea.dataservice')


class Widget(CWidget):
    """ Geographical coverage widget
    """
    widget_type = 'geocoverage'
    widget_label = 'European countries'
    groups = (
        DefaultSchemata,
        LayoutSchemata,
        CountableSchemata,
        DisplaySchemata
    )

    def query(self, form):
        """ Get value from form and return a catalog dict query
        """

        query = {}
        index = self.data.get('index', '')
        index = index.encode('utf-8', 'replace')
        if not index:
            return query


        if self.hidden:
            value = self.default
        else:
            value = form.get(self.data.getId(), '')

        if not value:
            return query
        countryGroups = getMultiAdapter(
            (self.context, self.request), name=u'getCountryGroups')()
        getCountriesByGroupView = getMultiAdapter(
            (self.context, self.request), name=u'getCountriesByGroupAsGeotags')

        if not isinstance(value, list):
            value = [value]

        tmp_value = []
        for code in value:
            if code in countryGroups:
                tmp_value.extend(getCountriesByGroupView(code))
            else:
                tmp_value.append(code)

        if getattr(self, 'operator_visible', False):
            operator = form.get(self.data.getId() + '-operator', self.operator)
        else:
            operator = self.operator
        query[index] = {'query': tmp_value, 'operator': operator}

        return query

    def portal_vocabulary(self):
        """ Return data vocabulary
        """
        #custom
        terms = []
        countryGroupsView = getMultiAdapter(
            (self.context, self.request), name=u'getCountryGroups')
        countriesView = getMultiAdapter(
            (self.context, self.request), name=u'getGeotagsCountries')

        terms.extend(countryGroupsView().items())
        terms.extend(countriesView())
        return terms

    def count(self, brains):
        """ Intersect results
        """
        res = {}
        sequence = [key for key, value in self.vocabulary()]
        if not sequence:
            return res

        index_id = self.data.get('index')
        if not index_id:
            return res

        ctool = getToolByName(self.context, 'portal_catalog')
        index = ctool._catalog.getIndex(index_id)
        apply_index = getattr(index, "_apply_index", None)
        if not apply_index:
            return res

        countryGroupsView = getMultiAdapter(
                (self.context, self.request), name=u'getCountryGroups')
        countryGroups = countryGroupsView()

        getCountriesByGroupView = getMultiAdapter(
                    (self.context, self.request), name=u'getCountriesByGroup')

        brains = IISet(brain.getRID() for brain in brains)
        for value in sequence:
            if not value:
                res[value] = len(brains)
                continue

            if value in countryGroups:
                gr_value = getCountriesByGroupView(value)
                rset = apply_index({
                    index_id: gr_value,
                    index_id +'_operator': self.operator,
                })
            else:
                rset = apply_index({
                    index_id: value
                })

            if not rset:
                continue
            rset, _u = rset
            rset = IISet(rset)
            _u, rset = weightedIntersection(brains, rset)
            if isinstance(value, str):
                value = value.decode('utf-8', 'replace')
            res[value] = len(rset)
        return res
