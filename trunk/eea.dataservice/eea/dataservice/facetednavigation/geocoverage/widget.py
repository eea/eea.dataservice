""" Geographical coverage widget
"""

from Products.CMFCore.utils import getToolByName
from BTrees.IIBTree import weightedIntersection, IISet
from eea.facetednavigation.widgets.select.widget import Widget as SelectWidget
from eea.facetednavigation.widgets.select.widget import EditSchema as SelectSchema


GeoSchema = SelectSchema.copy()
GeoSchema['vocabulary'].widget.visible = -1

class Widget(SelectWidget):
    """ Geographical coverage widget
    """
    widget_type = 'geocoverage'
    widget_label = 'European countries'
    edit_schema = GeoSchema

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

        # custom
        countryGroupsView = self.context.unrestrictedTraverse('@@getCountryGroups')
        if (value,value) in countryGroupsView():
            getCountriesByGroupView = self.context.unrestrictedTraverse('@@getCountriesByGroup')
            query[index] = {'query': getCountriesByGroupView(value), 'operator': 'and'}
        else:
            query[index] = value

        return query

    def portal_vocabulary(self):
        """ Return data vocabulary
        """
        #custom
        terms = []
        countryGroupsView = self.context.unrestrictedTraverse('@@getCountryGroups')
        countriesView = self.context.unrestrictedTraverse('@@getCountries')

        terms.extend(countryGroupsView())
        terms.extend(countriesView())

        return terms

    def apply_sequence(self, sequence, brains):
        """ Intersect results
        """
        if not sequence:
            return {}

        index_id = self.data.get('index')
        if not index_id:
            return {}

        ctool = getToolByName(self.context, 'portal_catalog')
        index = ctool._catalog.getIndex(index_id)
        apply_index = getattr(index, "_apply_index", None)
        if not apply_index:
            return {}

        res = {}

        brains = IISet(brain.getRID() for brain in brains)
        for value in sequence:
            if not value:
                res[value] = len(brains)
                continue

            #custom
            countryGroupsView = self.context.unrestrictedTraverse('@@getCountryGroups')
            if (value,value) in countryGroupsView():
                getCountriesByGroupView = self.context.unrestrictedTraverse('@@getCountriesByGroup')
                gr_value = getCountriesByGroupView(value)
                rset = apply_index({index_id: gr_value})
            else:
                rset = apply_index({index_id: value})

            if not rset:
                continue
            rset, u = rset
            rset = IISet(rset)
            u, rset = weightedIntersection(brains, rset)
            if isinstance(value, str):
                value = value.decode('utf-8', 'replace')
            res[value] = len(rset)
        return res
