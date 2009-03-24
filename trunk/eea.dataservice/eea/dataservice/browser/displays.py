import operator
from Products.CMFCore.utils import getToolByName


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

class OrganisationContainerView(object):
    """ Default organisation view
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

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
                res = ORGANISATION_SNIPPET % {'title': brain.Title,
                                              'url': brain.getUrl,
                                              'description': brain.Description}
        return res

class GetOrganisations(object):
    """ Organisations vocabulary
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        organisations = []
        cat = getToolByName(self.context, 'portal_catalog')
        res = cat.searchResults({'portal_type' : 'Organisation'})

        organisations.extend((brain.getUrl, brain.Title)
                             for brain in res)

        return sorted(organisations, key=operator.itemgetter(1))

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
      data.setValue(%(cindex)s, 1, 1);""" % {'cc': country_code, 'cindex': cc.index(country_code)}
                country_data += tmp
        return GEO_COVERAGE_MAP % (country_count, country_data)


ORGANISATION_SNIPPET = """
  <fieldset style="padding:0 1em 1em 1em; margin: 0 1em">
    <legend>
      <span style="cursor: pointer; margin:0.3em" title="Remove snippet" class="dummy-remove">[x]</span>Organisation snippet
    </legen>
    <h4>%(title)s</h4>
    <p>%(description)s</p>
    <a href="%(url)s">%(url)s</a>
  </fieldset>
"""

GEO_COVERAGE_MAP = """
    <script type='text/javascript' src='http://www.google.com/jsapi'></script>
    <script type='text/javascript'>
     google.load('visualization', '1', {'packages': ['geomap']});
     google.setOnLoadCallback(drawMap);

     function drawMap() {
        var data = new google.visualization.DataTable();
        data.addRows(%s);
        data.addColumn('string', 'Country');
        data.addColumn('number', 'Dataset coverage');
%s

        var options = {};
        options['dataMode'] = 'regions';
  
        var container = document.getElementById('map_canvas');
        var geomap = new google.visualization.GeoMap(container);
        geomap.draw(data, options);
    };
    </script>
"""
