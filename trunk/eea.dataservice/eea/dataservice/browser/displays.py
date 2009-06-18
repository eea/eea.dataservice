# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

import operator
from Products.CMFCore.utils import getToolByName
from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL
from Products.PloneLanguageTool.availablelanguages import getCountries
from eea.dataservice.vocabulary import COUNTRIES_DICTIONARY_ID
from eea.dataservice.vocabulary import QUALITY_DICTIONARY_ID

class DatasetContainerView(object):
    """ Default dataset view
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

class DatafileContainerView(object):
    """ Default datafile view
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

class DatatableContainerView(object):
    """ Default datatable view
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

class MainDatasets(object):
    """ Main datasets based on last modified and
        minimum 3 versions.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, count=2, ver_num=3):
        res = []
        cat = getToolByName(self, 'portal_catalog')
        brains = cat.searchResults({'portal_type' : ['Data'],
                                    'sort_on': 'modified',
                                    'sort_order': 'reverse'})

        for brain in brains:
            dataset = brain.getObject()
            versions_view = dataset.unrestrictedTraverse('@@getVersions')
            if len(versions_view()) > ver_num:
                res.append(dataset)
            if len(res) == count: break

        return res

class OrganisationContainerView(object):
    """ Default organisation view
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

def _getCountryName(country_code):
    """ """
    return getCountries().get(country_code.upper(), country_code)

def _getGroupCountries(context, group_code):
    """ """
    atvm = getToolByName(context, ATVOCABULARYTOOL)
    vocab = atvm[COUNTRIES_DICTIONARY_ID]
    terms = vocab.getVocabularyDict()
    for key in terms.keys():
        if group_code.lower() == terms[key][0].lower():
            return [term for term, childs in terms[key][1].values()]
    return []

def _getCountryInfo(context):
    """ """
    res = {'groups': {}, 'countries': {}}
    atvm = getToolByName(context, ATVOCABULARYTOOL)
    vocab = getattr(atvm, COUNTRIES_DICTIONARY_ID, None)
    if not vocab:
        return res

    terms = vocab.getVocabularyDict()
    for key in terms.keys():
        code = terms[key][0]
        if terms[key][1].keys():
            res['groups'][code] = code
        else:
            res['countries'][code] = _getCountryName(code)
    return res

class GetCountryGroups(object):
    """ """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        res = _getCountryInfo(self.context)['groups']
        return [(key, res[key]) for key in res.keys()]

class GetCountries(object):
    """ """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        countries = _getCountryInfo(self.context)['countries']
        res = [(key, countries[key]) for key in countries.keys()]
        return sorted(res, key=operator.itemgetter(1))

class GetCountryGroupsData(object):
    """ """
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
        return res

class GetCountriesByGroup(object):
    """ """
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

class GetCountriesDisplay(object):
    """ """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, country_codes=[]):
        data = []
        if country_codes == 'null': country_codes = []
        if not isinstance(country_codes, (list, tuple)):
            data.append(country_codes)
        else:
            data.extend(country_codes)
        res = []
        context = self.context
        viewGetCountryGroups = GetCountryGroups(context, self.request)
        for group_code, group_name in viewGetCountryGroups():
            tmp_match = _getGroupCountries(context, group_code)
            for country_code in data:
                if country_code in tmp_match:
                    tmp_match.remove(country_code)
            if not len(tmp_match): res.append(group_code)

        for group_code in res:
            group_countries = _getGroupCountries(context, group_code)
            for country_code in group_countries:
                if country_code in data:
                    data.remove(country_code)
                    if not len(data): break

        res_string = ''
        if len(res):
            res_string = ', '.join(res)
        if len(data):
            countries = []
            [countries.append(_getCountryName(code)) for code in data]
            countries.sort()
            if res_string:
                res_string += ', '
            res_string += ', '.join(countries)
        return res_string

class FormatTempCoverage(object):
    """ Format temporal coverage display
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        field = self.context.getField('temporalCoverage')
        data = field.getAccessor(self.context)()
        data = list(data)
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
                if not location: view = 'none'
                res = ORGANISATION_SNIPPET % {'title': brain.Title,
                                              'url': brain.getUrl,
                                              'address': location,
                                              'description': brain.Description,
                                              'view': view}
        return res

class GeographicalCoverageMap(object):
    """ Return geographical coverage map
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, cc):
        country_data = ''
        country_count = 0
        if cc:
            cc = list(cc)
            country_count = len(cc)
            for country_code in cc:
                tmp = """
      data.setValue(%(cindex)s, 0, '%(cc)s');
      data.setValue(%(cindex)s, 1, 1);""" % {'cc': country_code.upper(), 'cindex': cc.index(country_code)}
                country_data += tmp
        return GEO_COVERAGE_MAP % (country_count, country_data)

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

        template_style = [['cell1', 'white'], ['cell2', 'white'], ['cell3', 'white']]
        for k in range(int(value)):
            template_style[k][1] = 'LightGreen'
        template_style = dict(template_style)
        template_style['label'] = label
        return QUALITY_TEMPLATE % template_style

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
      <span style="color: red; cursor: pointer; margin:0.3em" title="Remove snippet" class="dummy-remove">[x]</span>Organisation snippet
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

GEO_COVERAGE_MAP = """
    <script type="text/javascript" src="http://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load("visualization", "1", {packages:["intensitymap"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
        var data = new google.visualization.DataTable();
        data.addColumn('string', '', 'Country');
        data.addColumn('number', 'Coverage', 'a');
        data.addRows(%s);
%s
        chart = new google.visualization.IntensityMap(document.getElementById('map_canvas'));
        chart.draw(data, {region:'europe',colors:['green']});
        jQuery('.google-visualization-intensitymap-legend').css("display","none");
        jQuery('.google-visualization-intensitymap-map').css("height","220px");
      }
    </script>
"""
