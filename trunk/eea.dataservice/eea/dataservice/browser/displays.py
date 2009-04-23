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
    atvm = getToolByName(context, ATVOCABULARYTOOL)
    vocab = atvm[COUNTRIES_DICTIONARY_ID]

    res = {'groups': {}, 'countries': {}}
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
        res = _getCountryInfo(self.context)['countries']
        return [(key, res[key]) for key in res.keys()]

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
        res = []
        context = self.context
        viewGetCountryGroups = GetCountryGroups(context, self.request)
        for group_code, group_name in viewGetCountryGroups():
            tmp_match = _getGroupCountries(context, group_code)
            for country_code in country_codes:
                if country_code in tmp_match:
                    tmp_match.remove(country_code)
            if not len(tmp_match): res.append(group_code)

        for group_code in res:
            group_countries = _getGroupCountries(context, group_code)
            for country_code in group_countries:
                if country_code in country_codes:
                    country_codes.remove(country_code)
                    if not len(country_codes): break

        res_string = ''
        if len(res):
            res_string = ', '.join(res)
        if len(country_codes):
            countries = []
            [countries.append(_getCountryName(code)) for code in country_codes]
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

    def __call__(self):
        return REFERENCE_SYSTEM_KUPU

class GetReferenceSystemTemplate(object):
    """ Return reference system templates
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, tpl):
        return REFERENCE_SYSTEM_TEMPLATES[tpl]

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

REFERENCE_SYSTEM_KUPU = """
<select name="reference-system-select" class="kupu-tb-styles" style="background-color:#ccc">
  <option value="ETRS89">ETRS89</option>
  <option value="ETRS">ETRS</option>
  <option value="Lambert">Lambert Azimutal</option>
  <option value="ALBERS">ALBERS</option>
  <option value="WGS">WGS</option>
</select>
"""

REFERENCE_SYSTEM_TEMPLATES = {
    'ETRS89': """
<table>
<tr>
<td valign="middle" colspan="2"><b>ETRS89</b> </td>
</tr>

<tr>
<td valign="top">Datum<br />
<span class="subscript">defines the position of the ellipsoid
(spheroid) relative to the center of the earth</span></td>
<td valign="top" class="subscript">D_ETRS_1989</td>
</tr>

<tr>
<td valign="top">Ellipsoid<br />
<span class="subscript">When used to represent the earth, the
three-dimensional shape obtained by rotating an ellipse about its
minor axis.</span></td>
<td valign="top" class="subscript">GRS_1980</td>
</tr>

<tr>
<td valign="top">Semi-major axis<br />
<span class="subscript">Radius of the equatorial axis of the
ellipsoid</span></td>
<td valign="top" class="subscript">6378137</td>
</tr>

<tr>
<td valign="top">Axis units<br />
<span class="subscript">Unit of the semi-major axis</span></td>
<td valign="top" class="subscript">Degrees</td>
</tr>

<tr>
<td valign="top">Flattening ratio<br />
<span class="subscript">Radius of the equatorial axis of the
ellipsoid</span></td>
<td valign="top" class="subscript">3.35281068118232E-03</td>
</tr>
</table>
""",
    'ETRS': """
<table>
<tr>
<td valign="middle" colspan="2"><b>ETRS - Lambert Azimutal Equal
Area</b></td>
</tr>

<tr>
<td valign="top">Datum<br />
<span class="subscript">defines the position of the ellipsoid
(spheroid) relative to the center of the earth</span></td>
<td valign="top" class="subscript">D_ETRS_1989</td>
</tr>

<tr>
<td valign="top">Ellipsoid<br />
<span class="subscript">When used to represent the earth, the
three-dimensional shape obtained by rotating an ellipse about its
minor axis.</span></td>
<td valign="top" class="subscript">GRS_1980</td>
</tr>

<tr>
<td valign="top">Semi-major axis<br />
<span class="subscript">Radius of the equatorial axis of the
ellipsoid</span></td>
<td valign="top" class="subscript">6378137</td>
</tr>

<tr>
<td valign="top">Axis units<br />
<span class="subscript">Unit of the semi-major axis</span></td>
<td valign="top" class="subscript">Degrees</td>
</tr>

<tr>
<td valign="top">Flattening ratio<br />
<span class="subscript">Radius of the equatorial axis of the
ellipsoid</span></td>
<td valign="top" class="subscript">3.35281068118232E-03</td>
</tr>

<tr>
<td valign="top">Projection<br />
<span class="subscript">a projected coordinate system designed for
two-dimensional surface mapping</span></td>
<td valign="top" class="subscript">Lambert_Azimutal_Equal_Area</td>
</tr>

<tr>
<td valign="top">False easting<br />
<span class="subscript">A linear value added to the x-coordinate
values, usually to ensure that all map coordinates are
positive.</span></td>
<td valign="top" class="subscript">4321000 meters</td>
</tr>

<tr>
<td valign="top">False northing<br />
<span class="subscript">A linear value added to the y-coordinate
values, usually to ensure that all map coordinates are
positive.</span></td>
<td valign="top" class="subscript">3210000 meters</td>
</tr>

<tr>
<td valign="top">Central median<br />
<span class="subscript">Line of longitude at the centre of a map
projection generally used as the basis for constructing the
projection</span></td>
<td valign="top" class="subscript">10 degrees</td>
</tr>

<tr>
<td valign="top">Latitude of origin<br />
<span class="subscript">Latitude chosen as the origin of
rectangular coordinates for a map projection</span></td>
<td valign="top" class="subscript">52 degrees</td>
</tr>
</table>
""",
    'Lambert': """
<table><tr><td valign="middle" colspan="2"><b>Lambert Azimutal</b></td></tr><tr><td valign="top">Longitute of Projection Center<br/><span  class="subscript">The longitude that defines the center (and sometimes origin) of a projection.</span></td><td valign="top">20°00'00''</td></tr><tr><td valign="top">Latitute of Projection Center<br/><span  class="subscript">The latitude that defines the center (and sometimes origin) of a projection.</span></td><td valign="top">52°00'00''</td></tr><tr><td valign="top">Ellipsoid<br/><span class="subscript">When used to represent the earth, the three-dimensional shape obtained by rotating an ellipse about its minor axis. This is an oblate ellipsoid of revolution, also called a spheroid. <b>sphere</b> A three-dimensional shape by revolving a circle arround its diameter.</span></td><td valign="top">Sphere: radius 6378137</td></tr><tr><td valign="top">Axis Units<br/><span class="subscript">Unit the x,y-coordinates are specified.</span></td><td valign="top">Meters</td></tr><tr><td valign="top">False Easting<br/><span class="subscript">A linear value added to the x-coordinate values, usually to ensure that all map coordinates are positive.</span></td><td valign="top">5071000.0 Meters</td></tr><tr><td valign="top">False Northing<br/><span class="subscript">A linear value added to the y-coordinate values, usually to ensure that all map coordinates are positive.</span></td><td valign="top">3210000.0 Meters</td></tr><tr><td valign="top">Semimajor Axis<br/><span class="subscript">The equatorial radius of a spheroid. Often known as "a"</span></td><td valign="top">6378137 Meters</td></tr></table>
""",
    'ALBERS': """
<table><tr><td valign="middle" colspan="2"><b>ALBERS Conical Equal Area</b></td></tr><tr><td valign="top">Longitute of Central Meridian<br/><span  class="subscript">The Longitute that defines the origin of the x-coordinate values for a projection.</span></td><td valign="top"> 22 39 00</td></tr><tr><td valign="top">Latitute of Projection Origin<br/><span  class="subscript">The latitute that defines the origin of the y-coordinate values for a projection</span></td><td valign="top">51 24 00</td></tr><tr><td valign="top">Ellipsoid<br/><span class="subscript">When used to represent the earth, the three-dimensional shape obtained by rotating an ellipse about its minor axis. This is an oblate ellipsoid of revolution, also called a spheroid. <b>sphere</b> A three-dimensional shape by revolving a circle arround its diameter.</span></td><td valign="top">Spheroid WGS72</td></tr><tr><td valign="top">Standard Parallel<br/><span class="subscript">The line of latitude where the projection surface touches the surface. A tangent conic or cylindrical projection has one standard parallel, while a secant conic or cylindrical projection has two. A standard parrallel has no distortion.</span></td><td valign="top">1st standard parallel 32 30 00, 2nd standard parallel 54 30 00</td></tr><tr><td valign="top">Axis Units<br/><span class="subscript">Unit the x,y-coordinates are specified.</span></td><td valign="top">Meters</td></tr><tr><td valign="top">False Easting<br/><span class="subscript">A linear value added to the x-coordinate values, usually to ensure that all map coordinates are positive.</span></td><td valign="top">0.0 Meters</td></tr><tr><td valign="top">False Northing<br/><span class="subscript">A linear value added to the y-coordinate values, usually to ensure that all map coordinates are positive.</span></td><td valign="top">0.0 Meters</td></tr><tr><td valign="top">Semimajor Axis<br/><span class="subscript">The equatorial radius of a spheroid. Often known as "a"</span></td><td valign="top">-</td></tr></table>
""",
    'WGS': """
<table><tr><td valign="middle" colspan="2"><b>WGS_1984_Web_Mercator</b></td></tr><tr><td valign="top" class="subscript">Ellipsoid<br/><span class="subscript">When used to represent the earth, the three-dimensional shape obtained by rotating an ellipse about its minor axis. This is an oblate ellipsoid of revolution, also called a spheroid. Sphere: a three-dimensional shape by revolving a circle arround its diameter.</span></td><td valign="top" class="subscript">D_WGS_1984</td></tr><tr><td valign="top">Standard parallel<br/><span class="subscript">The line of latitude where the projection surface touches the surface. A tangent conic or cylindrical projection has one standard parallel, while a secant conic or cylindrical projection has two. A standard parrallel has no distortion.</span></td><td valign="top" class="subscript">0.0</td></tr><tr><td valign="top">Axis units<br/><span class="subscript">The x,y-coordinates are specified.</span></td><td valign="top" class="subscript">Meters</td></tr><tr><td valign="top">False easting<br/><span class="subscript">A linear value added to the x-coordinate values, usually to ensure that all map coordinates are positive.</span></td><td valign="top" class="subscript">0.0 Meters</td></tr><tr><td valign="top">False northing<br/><span class="subscript">A linear value added to the y-coordinate values, usually to ensure that all map coordinates are positive.</span></td><td valign="top" class="subscript">0.0 Meters</td></tr><tr><td valign="top">Semi-major axis<br/><span class="subscript">The equatorial radius of a spheroid, Often known as "a"</span></td><td valign="top" class="subscript">6378137 Meters</td></tr></table>
"""
}