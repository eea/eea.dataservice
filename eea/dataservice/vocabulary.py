""" Vocabularies
"""
import logging
import operator
import eventlet
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IVocabularyFactory
from Products.CMFCore.utils import getToolByName
from eea.dataservice.config import ROD_SERVER, SOCKET_TIMEOUT
from eea.cache import cache as eeacache
from plone.memoize import request as cacherequest

logger = logging.getLogger('eea.dataservice.vocabulary')

# Main keywords vocabulary
class MainKeywords(object):
    """ Main keywords vocabulary
    """
    implements(IVocabularyFactory)

    def __call__(self, context=None):
        words_length = 30
        cat = getToolByName(context, 'portal_catalog')
        index = cat.Indexes.get('Subject', None)
        values = index.uniqueValues(name=None, withLengths=1)
        words = [k for k in values]
        words = sorted(words, key=operator.itemgetter(1))
        words = words[-words_length:]
        words = [SimpleTerm(w[0], w[0], w[0]) for w in words]
        return SimpleVocabulary(words)


# Coordinate reference system
REFERENCE_DICTIONARY_ID = 'reference_system'
REFERENCE_DICTIONARY = {}
REFERENCE_DICTIONARY[REFERENCE_DICTIONARY_ID] = (
    ('3035', 'EPSG:3035'),
    ('4008', 'EPSG:4008'),
    ('4258', 'EPSG:4258'),
    ('4326', 'EPSG:4326')
)

# Geographic quality
QUALITY_DICTIONARY_ID = 'quality'
QUALITY_DICTIONARY = {}
QUALITY_DICTIONARY[QUALITY_DICTIONARY_ID] = (
    ('Hidden', '-1'),
    ('Undefined', '0'),
    ('Poor', '1'),
    ('Good', '2'),
    ('Excellent', '3')
)

# Quick link vocabulary for datasets
QLD_DICTIONARY_ID = 'quick_links_ds'
QLD_DICTIONARY = {}
QLD_DICTIONARY[QLD_DICTIONARY_ID] = (
    ('air emissions', 'Air emissions'),
    ('air quality', 'Air quality'),
    ('CLC1990', 'Corine land cover 1990'),
    ('CLC2000', 'Corine land cover 2000'),
    ('EEA owned data sets', 'EEA owned data sets'),
    ('LEAC', 'Land cover accounts'),
    ('Eurosion', 'Eurosion'),
    ('CDDA', 'Nationally designated areas'),
    ('point data', 'Point data'),
    ('raster data', 'Raster data'),
    ('geospatial data', 'Geospatial data'),
    ('vector data', 'Vector data'),
    ('waterbase', 'Waterbase'),
    ('WISE', 'Wise', )
)

# Quick link vocabulary for maps and graphs
# TO DO: replace in the XML dump the keyword
#      "State of the environment report No 1/2007"
#      with "State of the environment report No 1 from 2007", as we cant add a
#      vocabulary with an ID containing / character

QLMG_DICTIONARY_ID = 'quick_links_mg'
QLMG_DICTIONARY = {}
QLMG_DICTIONARY[QLMG_DICTIONARY_ID] = (
    ('State of the environment report No 1 2007',
     "Europe's environment - The fourth assessment"),
    ('State and Outlook 2005', 'State and Outlook'),
    ('State and Outlook 2005 - Part A', 'State and Outlook - Part A'),
    ('State and Outlook 2005 - Part B', 'State and Outlook - Part B'),
    ('State and Outlook 2005 - Part C', 'State and Outlook - Part C'),
    ('CLC2000', 'Corine land cover 2000'),
    ('Eurosion', 'Eurosion')
)

# Categories vocabulary
CATEGORIES_DICTIONARY_ID = 'categories'
CATEGORIES_DICTIONARY = {}
CATEGORIES_DICTIONARY[CATEGORIES_DICTIONARY_ID] = (
    ('adin', 'Additional information'),
    ('dbco', 'Data by country (including raw data)'),
    ('docu', 'Documents'),
    ('edse', 'European data set'),
    ('edsx', 'European data set (XML format)'),
    ('gisd', 'GIS data'),
    ('hard', 'Hard copy'),
    ('meto', 'Methodology'),
    ('odata', 'Original data used to produce the analysis'),
    ('orig', 'Original work data'),
    ('stat', 'Statistics')
)

# Figures type vocabulary
class FigureTypes(object):
    """ Figure types vocabulary
    """
    implements(IVocabularyFactory)

    def __call__(self, context=None):
        items = [
            SimpleTerm('map', 'map', 'Map'),
            SimpleTerm('graph', 'graph', 'Graph')
        ]
        return SimpleVocabulary(items)

# Conversion format for EEAFigureFiles
CONVERSIONS_DICTIONARY_ID = 'conversions'
CONVERSIONS_DICTIONARY = {}
CONVERSIONS_DICTIONARY[CONVERSIONS_DICTIONARY_ID] = (
    ('GIF-400', 'High resolution GIF'), # public
    ('PNG-400', 'High resolution PNG'), # public
    ('PNG-300', 'Medium resolution PNG'), # public
    ('PNG-75', 'Low resolution PNG'),
    ('TIFF-400', 'High resolution TIFF'), # public
    ('PNG-96', 'Low resolution PNG'),
    ('GIF-96', 'Low resolution GIF'),
)
CONVERSIONS_USED = ['GIF-400', 'PNG-400', 'PNG-300', 'TIFF-400']

# Organisations vocabulary
def generateUniqueTitles(data):
    """ Unique titles
    """
    seen_titles = set()
    data_unique_titles = {}
    for url, orig_title in data.iteritems():
        n = 0
        title = orig_title
        while title in seen_titles:
            n += 1
            title = u'%s (%d)' % (orig_title, n)
        seen_titles.add(title)
        data_unique_titles[url] = title
    return data_unique_titles


class Organisations(object):
    """ Organisations
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        if hasattr(context, 'context'):
            context = context.context
        return self._organisations(context, context.REQUEST)

    @cacherequest.cache(lambda method, self, context, request: method)
    def _organisations(self, context, request):
        """ Organisations
        """
        unique_org = {}
        cat = getToolByName(context, 'portal_catalog')
        res = cat.searchResults({'portal_type': 'Organisation'})
        for brain in res:
            title = brain.Title.strip()
            if isinstance(title, str):
                try:
                    title = title.decode('utf-8')
                except Exception, err:
                    logger.exception(err)
                    title = brain.getId

            unique_org.setdefault(brain.getUrl, title)

        unique_org = generateUniqueTitles(unique_org)

        organisations = unique_org.items()
        organisations.sort(key=operator.itemgetter(1))

        items = [SimpleTerm(key, key, value) for key, value in organisations]
        return SimpleVocabulary(items)

# Obligations vocabulary
def formatTitle(title):
    """ Format title
    """
    res = title
    if len(title) > 70:
        res = title[:70]
        res += ' ...'
    return res


MEMCACHED_CACHE_SECONDS_KEY = 86400 # 1 day
@eeacache(lambda *args: MEMCACHED_CACHE_SECONDS_KEY)
def _obligations():
    """
    :return: cached results of Environmental reporting obligations server for
    24H cached in memcached
    """
    logger.log(logging.INFO, 'called obligations ROD server')
    res = {}
    xmlrpclib = eventlet.import_patched('xmlrpclib')

    with eventlet.timeout.Timeout(SOCKET_TIMEOUT):
        try:
            server = xmlrpclib.Server(ROD_SERVER)
            result = server.WebRODService.getActivities()
        except Exception, err:
            logger.exception(err)
            result = []

    for obligation in result:
        key = int(obligation['PK_RA_ID'])
        title = formatTitle(obligation['TITLE'])
        try:
            title = title.decode('utf-8')
        except UnicodeEncodeError, err:
            logger.warning("Obligation title found as unicode: %s", title)
            logger.warning(err)
        res[key] = title
    return res


class Obligations(object):
    """ Obligations
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        if hasattr(context, 'context'):
            context = context.context
        self.context = context
        # use cached results from ROD SERVER
        res = _obligations()

        items = res.items()
        items.sort()
        items = [SimpleTerm(str(key), str(key), value)
                 for key, value in items]
        items.insert(0, SimpleTerm(str(1), str(1), "Not applicable"))
        return SimpleVocabulary(items)


# Geographic coverage vocabulary
COUNTRIES_DICTIONARY_ID = 'european_countries'

def getCountriesDictionary():
    """ Countries
    """
    res = {}

    #european countries
    data = getCountries()
    for key in data:
        res[(key.lower(), data[key])] = {}

    # country groups
    res[('efta4', 'EFTA4')] = EFTA4
    res[('eu15', 'EU15')] = EU15
    res[('eu25', 'EU25')] = EU25
    res[('eu27', 'EU27')] = EU27
    return res

EFTA4 = {('ch', 'ch'): {},
        ('is', 'is'): {},
        ('li', 'li'): {},
        ('no', 'no'): {},
}
EU15 = {('at', 'at'): {},
        ('be', 'be'): {},
        ('de', 'de'): {},
        ('dk', 'dk'): {},
        ('es', 'es'): {},
        ('fi', 'fi'): {},
        ('fr', 'fr'): {},
        ('gb', 'gb'): {},
        ('gr', 'gr'): {},
        ('ie', 'ie'): {},
        ('it', 'it'): {},
        ('lu', 'lu'): {},
        ('nl', 'nl'): {},
        ('pt', 'pt'): {},
        ('se', 'se'): {},
}
EU25 = {('at', 'at'): {},
        ('be', 'be'): {},
        ('cy', 'cy'): {},
        ('cz', 'cz'): {},
        ('de', 'de'): {},
        ('dk', 'dk'): {},
        ('ee', 'ee'): {},
        ('es', 'es'): {},
        ('fi', 'fi'): {},
        ('fr', 'fr'): {},
        ('gb', 'gb'): {},
        ('gr', 'gr'): {},
        ('hu', 'hu'): {},
        ('ie', 'ie'): {},
        ('it', 'it'): {},
        ('lt', 'lt'): {},
        ('lu', 'lu'): {},
        ('lv', 'lv'): {},
        ('mt', 'mt'): {},
        ('nl', 'nl'): {},
        ('pl', 'pl'): {},
        ('pt', 'pt'): {},
        ('se', 'se'): {},
        ('si', 'si'): {},
        ('sk', 'sk'): {},
}
EU27 = {('at', 'at'): {},
        ('be', 'be'): {},
        ('bg', 'bg'): {},
        ('cy', 'cy'): {},
        ('cz', 'cz'): {},
        ('de', 'de'): {},
        ('dk', 'dk'): {},
        ('ee', 'ee'): {},
        ('es', 'es'): {},
        ('fi', 'fi'): {},
        ('fr', 'fr'): {},
        ('gb', 'gb'): {},
        ('gr', 'gr'): {},
        ('hu', 'hu'): {},
        ('ie', 'ie'): {},
        ('it', 'it'): {},
        ('lt', 'lt'): {},
        ('lu', 'lu'): {},
        ('lv', 'lv'): {},
        ('mt', 'mt'): {},
        ('nl', 'nl'): {},
        ('pl', 'pl'): {},
        ('pt', 'pt'): {},
        ('ro', 'ro'): {},
        ('se', 'se'): {},
        ('si', 'si'): {},
        ('sk', 'sk'): {},
}

def getCountries():
    """ European countries """
    # In case we need all countries:
    #from Products.PloneLanguageTool.availablelanguages import getCountries
    #return getCountries()

    return {
        'ad':'ad',
        'al':'al',
        'am':'am',
        'at':'at',
        'az':'az',
        'ba':'ba',
        'be':'be',
        'bg':'bg',
        'by':'by',
        'ch':'ch',
        #'cs':'cs', #Serbia and Montenegro, not used
        'cy':'cy',
        'cz':'cz',
        'de':'de',
        'dk':'dk',
        'ee':'ee',
        'es':'es',
        'fi':'fi',
        #'fo':'fo', #Faroe Islands, not used
        'fr':'fr',
        'gb':'gb',
        'ge':'ge',
        'gr':'gr',
        'hr':'hr',
        'hu':'hu',
        'ie':'ie',
        #'il':'il', #Israel, not used
        'is':'is',
        'it':'it',
        'kz':'kz',
        'li':'li',
        'lt':'lt',
        'lu':'lu',
        'lv':'lv',
        'mc':'mc',
        'md':'md',
        'me':'me',
        'mk':'mk',
        'mt':'mt',
        'nl':'nl',
        'no':'no',
        'pl':'pl',
        'pt':'pt',
        'ro':'ro',
        'rs':'rs',
        'ru':'ru',
        'se':'se',
        'si':'si',
        'sk':'sk',
        'sm':'sm',
        'tr':'tr',
        'ua':'ua',
        }
