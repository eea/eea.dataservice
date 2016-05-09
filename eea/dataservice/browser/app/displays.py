""" Displays
"""
import operator
import json
from zope.component import queryMultiAdapter, queryAdapter, getUtility
from Products.CMFCore.utils import getToolByName
from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL
from plone.i18n.locales.interfaces import ICountryAvailability
from DateTime import DateTime
from eea.dataservice.relations import IRelations
from eea.dataservice.vocabulary import (
    QUALITY_DICTIONARY_ID,
    COUNTRIES_DICTIONARY_ID,
    CATEGORIES_DICTIONARY_ID)
from eea.dataservice.vocabulary import eeacache, MEMCACHED_CACHE_SECONDS_KEY
from eea.dataservice.vocabulary import _obligations
from eea.versions.interfaces import IGetVersions
from plone.memoize import request as cacherequest


try:
    from eea.reports import interfaces as ireport

    IReportContainerEnhanced = ireport.IReportContainerEnhanced
except ImportError:
    from zope.interface import Interface

    class IReportContainerEnhanced(Interface):
        """ eea.reports is not present """


class OrganisationStatistics(object):
    """ Returns number of owners and processors pointing to this organisation
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getOnlyLastVersion(self, brains):
        """ Filter brains to get only last versions
        """
        last_versions = {}
        brains = [brain for brain in brains]
        for brain in brains:
            version_id = getattr(brain, 'getVersionId', '')
            if version_id:
                effective_date = getattr(brain, 'EffectiveDate', DateTime(1970))
                if len(version_id):
                    if last_versions.has_key(version_id):
                        current_date = getattr(
                            last_versions[version_id], 'EffectiveDate',
                            DateTime(1970))
                        if current_date < effective_date:
                            last_versions[version_id] = brain
                    else:
                        last_versions[version_id] = brain

        versions = [k.data_record_id_ for k in last_versions.values()]
        for brain in brains:
            version_id = getattr(brain, 'getVersionId', '')
            if version_id:
                if brain.data_record_id_ in versions:
                    yield brain
            else:
                yield brain

    def __call__(self):
        data = {'owners': ([], [], [], [], [], []), 'processor': ([], [])}
        cat = getToolByName(self.context, 'portal_catalog')
        memtool = getToolByName(self.context, 'portal_membership')
        query = {}

        # Only published content for authenticated
        if memtool.isAnonymousUser():
            query['review_state'] = 'published'
            query['effectiveRange'] = DateTime()

        # Owner statistics
        query['portal_type'] = 'Specification'
        query['getOwnership'] = self.context.org_url()
        brains = cat.searchResults(query)
        data['owners'][5].extend(self.getOnlyLastVersion(brains))

        query['portal_type'] = 'Assessment'
        query['getOwnership'] = self.context.org_url()
        brains = cat.searchResults(query)
        data['owners'][4].extend(self.getOnlyLastVersion(brains))
        del query['getOwnership']

        query['portal_type'] = 'DavizVisualization'
        query['getDataOwner'] = self.context.org_url()
        brains = cat.searchResults(query)
        data['owners'][3].extend(self.getOnlyLastVersion(brains))

        query['portal_type'] = 'ExternalDataSpec'
        query['getDataOwner'] = self.context.org_url()
        brains = cat.searchResults(query)
        data['owners'][2].extend(self.getOnlyLastVersion(brains))

        query['portal_type'] = 'EEAFigure'
        query['getDataOwner'] = self.context.org_url()
        brains = cat.searchResults(query)
        data['owners'][1].extend(self.getOnlyLastVersion(brains))

        query['portal_type'] = 'Data'
        query['getDataOwner'] = self.context.org_url()
        brains = cat.searchResults(query)
        data['owners'][0].extend(self.getOnlyLastVersion(brains))
        del query['getDataOwner']

        # Processor statistics
        query['portal_type'] = 'EEAFigure'
        query['getProcessor'] = self.context.org_url()
        brains = cat.searchResults(query)
        data['processor'][1].extend(self.getOnlyLastVersion(brains))

        query['portal_type'] = 'Data'
        query['getProcessor'] = self.context.org_url()
        brains = cat.searchResults(query)
        data['processor'][0].extend(self.getOnlyLastVersion(brains))

        return data


class DisplaySize(object):
    """ Transform a file size in Kb, Mb ..
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, size=0):
        size = float(size)
        if size >= 1000:
            size /= 1024
            ftype = 'KB'
            if size >= 1000:
                size /= 1024
                ftype = 'MB'
            res = '%s %s' % ('%4.2f' % size, ftype)
        else:
            ftype = 'Bytes'
            res = '%s %s' % ('%4.0f' % size, ftype)
        return res


class GetDataForRedirect(object):
    """ Get objects to redirect
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, query=None):
        if query is None:
            query = {}
        res = []
        cat = getToolByName(self.context, 'portal_catalog')
        res = cat(**query)
        if not res:
            # If no results published try searching for objects
            # in published_eionet state
            query['review_state'] = ['published', 'published_eionet']
            res = cat.unrestrictedSearchResults(**query)
        return res


class GetCategoryName(object):
    """ Return category name
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, cat_code):
        try:
            vocab = _categories_vocabulary(self, self.request)
            return getattr(vocab, cat_code).Title()
        except AttributeError:
            return 'Category name'


class DatasetBasedOn(object):
    """ Returns 'based on' datasets
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        relations = queryAdapter(self.context, IRelations)
        if not relations:
            return []

        return [rel for rel in relations.backReferences()
                if rel.portal_type == 'Data']


class DatasetDerivedFrom(object):
    """ Returns 'derived from' datasets
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        relations = queryAdapter(self.context, IRelations)
        if not relations:
            return []

        return [rel for rel in relations.forwardReferences()
                if rel.portal_type == 'Data']


class Obligations(object):
    """ Returns obligations
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return _obligations()


class MainDatasets(object):
    """ Main datasets based on last modified and
        minimum 3 versions.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, count=5, ver_num=3):
        res = []
        cat = getToolByName(self.context, 'portal_catalog')
        brains = cat.searchResults({'portal_type': ['Data'],
                                    'sort_on': 'modified',
                                    'sort_order': 'reverse',
                                    'review_state': 'published'})

        for brain in brains:
            dataset = brain.getObject()
            api = IGetVersions(dataset)
            versions = api.versions()
            versions_num = len(versions)
            if versions_num > ver_num:
                latest_version = api.latest_version()
                if not latest_version in res:
                    res.append(latest_version)
            if len(res) == count:
                break

        return res


class DataViewers(object):
    """ Return top 5 latest published interactive Data Viewers
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        #res = []
        limit = 5
        cat = getToolByName(self, 'portal_catalog')
        brains = cat.searchResults({'object_provides':
            ['Products.EEAContentTypes.content.interfaces.IInteractiveData'],
            'sort_on': 'effective',
            'sort_order': 'reverse',
            'review_state': 'published'})[:limit]
        res = [brain.getObject() for brain in brains]
        return res


def _getCountryName(country_code, countries=None):
    """ Country Name
    """
    if countries is None:
        util = getUtility(ICountryAvailability)
        countries = util.getCountries()
    res = countries.get(country_code.lower(), {})
    res = res.get('name', country_code)
    return res


def _getGroupCountries(context, group_code):
    """ Group Countries
    """
    terms = _country_terms(context)
    for key in terms.keys():
        if group_code.lower() == terms[key][0].lower():
            return [term for term, _childs in terms[key][1].values()]
    return []


def cache_key(method, self, request):
    """ cache_key for request cache expecting a method and a request instance
    """
    return MEMCACHED_CACHE_SECONDS_KEY

@cacherequest.cache(cache_key)
def _categories_vocabulary(self, request):
    """ Cache categories vocabulary for the duration of the request
    """
    atvm = getToolByName(self.context, ATVOCABULARYTOOL)
    return atvm[CATEGORIES_DICTIONARY_ID]


@eeacache(lambda * args: MEMCACHED_CACHE_SECONDS_KEY)
def _getCountryInfo(context):
    """ Country Info
    """
    res = {'groups': {}, 'countries': {}}
    terms = _country_terms(context)
    if not terms:
        return res

    util = getUtility(ICountryAvailability)
    countries = util.getCountries()

    for key in terms.keys():
        code = terms[key][0]
        if terms[key][1].keys():
            res['groups'][code] = code
        else:
            res['countries'][code] = _getCountryName(code, countries)
    return res


@eeacache(lambda *args: MEMCACHED_CACHE_SECONDS_KEY)
def _country_terms(context):
    """ Cache the value of the countries dictionary
    """
    atvm = getToolByName(context, ATVOCABULARYTOOL)
    vocab = getattr(atvm, COUNTRIES_DICTIONARY_ID, None)
    return vocab.getVocabularyDict()


class GetCountryGroups(object):
    """ Country Groups
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return _getCountryInfo(self.context)['groups']


class GetCountries(object):
    """ Countries
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        countries = _getCountryInfo(self.context)['countries']
        res = [(key, countries[key]) for key in countries.keys()]
        return sorted(res, key=operator.itemgetter(1))


class GetGeotagsCountries(object):
    """ Countries where the key and title  represent the country name
            as used by the location field
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        countries = _getCountryInfo(self.context)['countries']
        res = [(countries[key], countries[key]) for key in countries.keys()]
        return sorted(res, key=operator.itemgetter(1))


class GetCountryGroupsData(object):
    """ Country Groups Data
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, group_id=''):
        res = {}
        terms = _country_terms(self)
        for key in terms.keys():
            if terms[key][1].keys():
                res[terms[key][0]] = []
                for c_key in terms[key][1].keys():
                    res[terms[key][0]].append(terms[key][1][c_key][0])
        return json.dumps(res)


class GetCountriesByGroup(object):
    """ Countries by group
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, group_id=''):
        res = []
        terms = _country_terms(self)
        for key in terms.keys():
            if terms[key][0] == group_id:
                for c_key in terms[key][1].keys():
                    res.append(terms[key][1][c_key][0])
                break
        return res


class GetCountriesByGroupAsGeotags(object):
    """ Countries by group with the country name set as
             key and value
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, group_id=''):
        res = []
        terms = _country_terms(self)
        util = getUtility(ICountryAvailability)
        countries = util.getCountries()
        for key in terms.keys():
            if terms[key][0] == group_id:
                for c_key in terms[key][1].keys():
                    res.append(countries.get(terms[key][1][c_key][0])['name']
                               .encode('utf-8'))
                break
        return res

class GetDataFiles(object):
    """ Return DataFile objects sorted by the position of the objects within
        their parent
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        cat = getToolByName(self.context, 'portal_catalog')
        brains = cat(
            portal_type=['DataFile'],
            path='/'.join(self.context.getPhysicalPath()),
            sort_on='getObjPositionInParent',
            show_inactive=True
        )
        if not brains:
            return False
        res = [brain.getObject() for brain in brains]

        return res


class GetDataFileLinks(object):
    """ Return DataFileLinks objects. These are links to external files
        sorted by the position of the objects within their parent
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        cat = getToolByName(self.context, 'portal_catalog')
        brains = cat(
            portal_type=['DataFileLink'],
            path='/'.join(self.context.getPhysicalPath()),
            sort_on='getObjPositionInParent',
            show_inactive=True
        )
        if not brains:
            return False
        res = [brain.getObject() for brain in brains]

        return res


class GetTablesByCategory(object):
    """ Return categories and related files sorted by the position of the
        objects within their parent
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        res = {}
        cat = getToolByName(self.context, 'portal_catalog')
        brains = cat(
            portal_type=['DataTable'],
            path='/'.join(self.context.getPhysicalPath()),
            sort_on='getObjPositionInParent',
            show_inactive=True
        )

        # Get DataTable files
        for brain in brains:
            table = brain.getObject()
            cat = table.category
            if not cat in res.keys():
                res[cat] = []
            res[cat].append(table)

        # Get sorted categories (based on vocabulary items order)
        categories = _categories_vocabulary(self, self.request)

        return (categories.keys(), res)

class GetOrganisationSnippet(object):
    """ Organisation snippet
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        res = None
        org_url = self.request.get('url', None)
        if org_url is not None:
            cat = getToolByName(self.context, 'portal_catalog')
            res = cat.searchResults({'portal_type': 'Organisation',
                                     'getUrl': org_url})
            if res:
                # Generate snippet
                brain = res[0]
                view = 'block'
                location = brain.location
                if not location:
                    view = 'none'
                elif isinstance(location, tuple):
                    location = location[0]
                res = ORGANISATION_SNIPPET % {
                    'title': brain.Title,
                    'url': brain.getUrl,
                    'address': location,
                    'description': brain.Description,
                    'view': view
                }
        return res


class GeographicalCoverageMap(object):
    """ Return geographical coverage map
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, cc):
        res = ''
        if cc:
            cc_list = ':2,'.join(cc) + ':2'
            res = ("http://map.eea.europa.eu/getmap.asp?Fullextent=1&"
                   "size=W200&PredefShade=Dataservice&Q=%s" % cc_list)
        return res


class GetReferenceSystemKupu(object):
    """ Return reference system select for Kupu
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request


class GetReferenceSystemTemplate(object):
    """ Return reference system templates
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request


class GetQualityDisplay(object):
    """ Return quality display
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, value):
        label = ''
        atvm = getToolByName(self.context, ATVOCABULARYTOOL)
        vocab = atvm[QUALITY_DICTIONARY_ID]
        terms = vocab.getVocabularyDict()
        for key in terms.keys():
            if terms[key] == value:
                label = key
                break

        template_style = [
            ['cell1', 'white'],
            ['cell2', 'white'],
            ['cell3', 'white']
        ]

        for k in range(int(value)):
            template_style[k][1] = 'LightGreen'
        template_style_dict = dict(template_style)
        template_style_dict['label'] = label
        return QUALITY_TEMPLATE % template_style_dict


class GetEEAFigureFiles(object):
    """ Returns 'based on' figures
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._figures = []

    @property
    def children(self):
        """ EEAFigure children property
        """
        return self.context.objectValues(['EEAFigureFile', 'ATLink'])

    def figures(self):
        """ Figures
        """
        if self._figures:
            return self._figures

        for doc in self.children:
            imgview = queryMultiAdapter((doc, self.request), name=u'imgview')
            if not imgview:
                continue
            if not imgview.display():
                continue
            self._figures.append(doc)

        return self._figures

    def singlefigure(self):
        """ Figure
        """
        figures = self.figures()
        if len(figures) == 1:
            return figures[0]
        return None

    def categories(self):
        """ Categories
        """
        res = {}
        singlefigure = self.singlefigure()
        for doc in self.children:
            if doc == singlefigure:
                continue

            if doc.portal_type == 'DataFileLink':
                # DataFileLink mapped under 'Documents'
                categ = 'docu'
                res.setdefault(categ, [])
                res[categ].append(doc)
            else:
                categ = doc.getCategory()
                res.setdefault(categ, [])
                res[categ].append(doc)

        for categ, doc in res.items():
            yield categ, doc


class MainFigures(object):
    """ Main figures based on last modified and
        minimum 3 versions.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, count=5, ver_num=3):
        res = []
        cat = getToolByName(self.context, 'portal_catalog')
        brains = cat.searchResults({'portal_type': ['EEAFigure'],
                                    'sort_on': 'modified',
                                    'sort_order': 'reverse',
                                    'review_state': 'published'})

        for brain in brains:
            figure = brain.getObject()
            api = IGetVersions(figure)
            versions = api.versions()
            versions_num = len(versions)
            if versions_num > ver_num:
                latest_version = api.latest_version()
                if not latest_version in res:
                    res.append(latest_version)
            if len(res) == count:
                break

        return res


QUALITY_TEMPLATE = """
<div>
    <table class="quality-table"><tbody><tr>
        <td style="background-color: %(cell1)s">&nbsp;&nbsp;</td>
        <td style="background-color: %(cell2)s">&nbsp;&nbsp;</td>
        <td style="background-color: %(cell3)s">&nbsp;&nbsp;</td>
    </tr></tbody></table>
    <span>%(label)s</span>
</div>
"""

ORGANISATION_SNIPPET = """
  <fieldset style="padding:0 1em 1em 1em; margin: 0 1em">
    <legend>
      <span style="color: red; cursor: pointer; margin:0.3em"
            title="Remove snippet"
            class="dummy-remove">[x]</span> Organisation snippet
    </legen>
    <h4>%(title)s</h4>
    <p>%(description)s</p>
    <a href="%(url)s">%(url)s</a>
    <p style="margin-top: 1em; display: %(view)s">
      <strong>Address:</strong>
      <span>%(address)s</span>
    </p>
  </fieldset>
"""
