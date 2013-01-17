""" Displays
"""
import operator
import xmlrpclib
import json
from zope.component import queryMultiAdapter, queryAdapter, getUtility
from Products.CMFCore.utils import getToolByName
from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL
from plone.i18n.locales.interfaces import ICountryAvailability
from DateTime import DateTime
from eea.dataservice.config import ROD_SERVER
from eea.dataservice.relations import IRelations
from eea.dataservice.vocabulary import (
    QUALITY_DICTIONARY_ID,
    COUNTRIES_DICTIONARY_ID,
    CATEGORIES_DICTIONARY_ID
)

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
            size = size/1024
            ftype = 'KB'
            if size >= 1000:
                size = size/1024
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
            query['review_state'] = ['published', \
                                     'published_eionet']
            res = cat.unrestrictedSearchResults(**query)
        return res

class GetCategoryName(object):
    """ Return category name
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, cat_code):
        atvm = getToolByName(self.context, ATVOCABULARYTOOL)
        vocab = atvm[CATEGORIES_DICTIONARY_ID]
        return getattr(vocab, cat_code).Title()

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
        res = {}
        server = xmlrpclib.Server(ROD_SERVER)
        result = server.WebRODService.getActivities()
        if result:
            for obligation in result:
                res[int(obligation['PK_RA_ID'])] =obligation['TITLE']
        return res

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
        brains = cat.searchResults({'portal_type' : ['Data'],
                                    'sort_on': 'modified',
                                    'sort_order': 'reverse',
                                    'review_state':'published'})

        for brain in brains:
            dataset = brain.getObject()
            versions_view = dataset.unrestrictedTraverse('@@getVersions')
            versions = versions_view()
            versions_num = len(versions)
            if versions_num > ver_num:
                latest_version = versions[versions_num]
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
        brains = cat.searchResults({'object_provides' : ['Products.EEAContentTypes.content.interfaces.IInteractiveData'],
                                    'sort_on': 'effective',
                                    'sort_order': 'reverse',
                                    'review_state': 'published'})[:limit]
        res = [brain.getObject() for brain in brains]
        return res

def _getCountryName(country_code, countries=None):
    """ Country Name
    """
    if countries == None:
        util = getUtility(ICountryAvailability)
        countries = util.getCountries()
    res = countries.get(country_code.lower(), {})
    res = res.get('name', country_code)

    if res.lower() == 'me':
        res = 'Montenegro'
    elif res.lower() == 'rs':
        res = 'Serbia'
    elif res.lower() == 'xk':
        res = 'Kosovo'
    return res

def _getGroupCountries(context, group_code):
    """ Group Countries
    """
    atvm = getToolByName(context, ATVOCABULARYTOOL)
    vocab = atvm[COUNTRIES_DICTIONARY_ID]
    terms = vocab.getVocabularyDict()
    for key in terms.keys():
        if group_code.lower() == terms[key][0].lower():
            return [term for term, _childs in terms[key][1].values()]
    return []

def _getCountryInfo(context):
    """ Country Info
    """
    res = {'groups': {}, 'countries': {}}
    atvm = getToolByName(context, ATVOCABULARYTOOL)
    vocab = getattr(atvm, COUNTRIES_DICTIONARY_ID, None)
    if not vocab:
        return res

    util = getUtility(ICountryAvailability)
    countries = util.getCountries()

    terms = vocab.getVocabularyDict()
    for key in terms.keys():
        code = terms[key][0]
        if terms[key][1].keys():
            res['groups'][code] = code
        else:
            res['countries'][code] = _getCountryName(code, countries)
    return res

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

class GetCountryGroupsData(object):
    """ Country Groups Data
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, group_id=''):
        atvm = getToolByName(self.context, ATVOCABULARYTOOL)
        vocab = atvm[COUNTRIES_DICTIONARY_ID]

        res = {}
        terms = vocab.getVocabularyDict()
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
        atvm = getToolByName(self.context, ATVOCABULARYTOOL)
        vocab = atvm[COUNTRIES_DICTIONARY_ID]

        res = []
        terms = vocab.getVocabularyDict()
        for key in terms.keys():
            if terms[key][0] == group_id:
                for c_key in terms[key][1].keys():
                    res.append(terms[key][1][c_key][0])
                break
        return res

class GetDataFiles(object):
    """ Return DataFile objects """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        cat = getToolByName(self.context, 'portal_catalog')
        brains = cat.searchResults({
            'portal_type' : ['DataFile'],
            'path': '/'.join(self.context.getPhysicalPath()),
            'review_state': 'published'})
        res = [brain.getObject() for brain in brains]

        # Sort DataFiles by filename
        comp = lambda x, y: cmp(x.getFilename(), y.getFilename())
        res.sort(comp)
        return res

class GetDataFileLinks(object):
    """ Return DataFileLinks objects. These are links to external files. """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        cat = getToolByName(self.context, 'portal_catalog')
        brains = cat.searchResults({
            'portal_type' : ['DataFileLink'],
            'path': '/'.join(self.context.getPhysicalPath()),
            'review_state': 'published'})
        res = [brain.getObject() for brain in brains]

        # Sort by title
        comp = lambda x, y: cmp(x.Title(), y.Title())
        res.sort(comp)
        return res

class GetTablesByCategory(object):
    """ Return categories and related files """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        res = {}
        cat = getToolByName(self.context, 'portal_catalog')
        brains = cat.searchResults({
            'portal_type': ['DataTable'],
            'path': '/'.join(self.context.getPhysicalPath()),
            'sort_on': 'sortable_title',
            'review_state':'published'
        })

        # Get DataTable files
        for brain in brains:
            table = brain.getObject()
            cat = table.category
            if not cat in res.keys():
                res[cat] = []
            res[cat].append(table)

        # Get sorted categories (based on vocabulary items order)
        atvm = getToolByName(self.context, ATVOCABULARYTOOL)
        categories = atvm[CATEGORIES_DICTIONARY_ID]

        return (categories.keys(), res)

class FormatTempCoverage(object):
    """ Format temporal coverage display
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        field = self.context.getField('temporalCoverage')
        data = field.getAccessor(self.context)()
        data = sorted(list(data))

        #in one odd case, the data is sorted in the wrong way, so we reverse
        #only if we need to
        if len(data) > 1 and (int(data[-1]) < int(data[0])):
            data.reverse()

        tmp_res = []
        res = ''

        for index, year in enumerate(data):
            if len(tmp_res) == 0:
                tmp_res.append(str(year))
            else:
                if int(data[index-1]) + 1 == int(year):
                    tmp_res.append('-%s' % str(year))
                else:
                    tmp_res.append(str(year))

        for index, year in enumerate(tmp_res):
            if index == 0:
                res += year
            elif index+1 == len(tmp_res):
                res += ', %s' % year
            elif not year.startswith('-'):
                res += ', %s' % year
            elif not tmp_res[index+1].startswith('-'):
                res += ', %s' % year
            elif year.startswith('-') and not tmp_res[index+1].startswith('-'):
                res += ', %s' % year
            elif year.startswith('-') and tmp_res[index+1].startswith('-'):
                pass
        return res.replace(', -', '-')

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
            res = cat.searchResults({'portal_type' : 'Organisation',
                                     'getUrl': org_url})
            if res:
                # Generate snippet
                brain = res[0]
                view = 'block'
                location = brain.location
                if not location:
                    view = 'none'
                elif type(location) == tuple:
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
        template_style = dict(template_style)
        template_style['label'] = label
        return QUALITY_TEMPLATE % template_style

class GetEEAFigureFiles(object):
    """ Returns 'based on' figures
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._brains = []
        self._figures = []

    @property
    def brains(self):
        """ ZCatalog brains
        """
        if not self._brains:
            self._brains = self.context.getFolderContents(contentFilter={
                'portal_type': 'EEAFigureFile',
                #'review_state': ['published','visible']
            })
        return self._brains

    def figures(self):
        """ Figures
        """
        if self._figures:
            return self._figures

        for brain in self.brains:
            doc = brain.getObject()
            imgview = queryMultiAdapter((doc, self.request), name=u'imgview')
            if not imgview:
                continue
            if not imgview.display():
                continue
            self._figures.append(brain)

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
        for brain in self.brains:
            if brain is singlefigure:
                continue
            doc = brain.getObject()
#            import pdb; pdb.set_trace()
            categ = doc.getCategory()
            res.setdefault(categ, [])
            res[categ].append(brain)

        for categ, brains in res.items():
            yield categ, brains

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
        brains = cat.searchResults({'portal_type' : ['EEAFigure'],
                                    'sort_on': 'modified',
                                    'sort_order': 'reverse',
                                    'review_state':'published'})

        for brain in brains:
            figure = brain.getObject()
            versions_view = figure.unrestrictedTraverse('@@getVersions')
            versions = versions_view()
            versions_num = len(versions)
            if versions_num > ver_num:
                latest_version = versions[versions_num]
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
