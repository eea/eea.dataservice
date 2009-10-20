# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

import operator
import xmlrpclib
from datetime import datetime

from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from zope.schema.vocabulary import SimpleVocabulary
from zope.app.schema.vocabulary import IVocabularyFactory
from Products.Archetypes.interfaces.vocabulary import IVocabulary

from eea.dataservice.config import *

# Temporal coverage vocabulary
class DatasetYears:
    """
    """
    __implements__ = (IVocabulary,)

    def getDisplayList(self, instance):
        """ """
        now = datetime.now()
        #end_year = now.year + 3
        end_year = 2099
        terms = []
        terms.extend((str(key), str(key))
                     for key in reversed(range(STARTING_YEAR, end_year)))
        return terms

    def getVocabularyDict(self, instance):
        return {}

    def isFlat(self):
        return False

    def showLeafsOnly(self):
        return False

class DatasetYearsVocabularyFactory(object):
    """ Dataset years vocabulary
    """
    implements(IVocabularyFactory)

    def __call__(self, context=None):
        data = DatasetYears().getDisplayList(context)
        return SimpleVocabulary.fromItems(data)

DatasetYearsVocabulary = DatasetYearsVocabularyFactory()

# Main keywords vocabulary
class MainKeywords:
    """
    """
    __implements__ = (IVocabulary,)

    def getDisplayList(self, instance):
        """ """
        words_length = 30
        words = []
        res = []
        cat = getToolByName(instance, 'portal_catalog')
        index = cat.Indexes.get('Subject', None)
        values = index.uniqueValues(name=None, withLengths=1)
        [words.append(k) for k in values]
        words = sorted(words, key=operator.itemgetter(1))
        words = words[-words_length:]
        [res.append((k[0], k[0])) for k in words]
        return res

    def getVocabularyDict(self, instance):
        return {}

    def isFlat(self):
        return False

    def showLeafsOnly(self):
        return False

class MainKeywordsVocabularyFactory(object):
    """ Main keywords vocabulary
    """
    implements(IVocabularyFactory)

    def __call__(self, context=None):
        data = MainKeywords().getDisplayList(context)
        return SimpleVocabulary.fromItems(data)

MainKeywordsVocabulary = MainKeywordsVocabularyFactory()

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
    ('Air emissions', 'Air emissions'),
    ('Air quality', 'Air quality'),
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
#TODO: replace in the XML dump the keyword "State of the environment report No 1/2007"
#      with "State of the environment report No 1 from 2007", as we cant add a
#      vocabulary with an ID containing / character

QLMG_DICTIONARY_ID = 'quick_links_mg'
QLMG_DICTIONARY = {}
QLMG_DICTIONARY[QLMG_DICTIONARY_ID] = (
    ('State of the environment report No 1 2007', "Europe's environment - The fourth assessment"),
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
    ('invi', 'Interactive viewers'),
    ('meto', 'Methodology'),
    ('odata', 'Original data used to produce the analysis'),
    ('orig', 'Original work data'),
    ('repo', 'Published in the following report(s)'),
    ('rews', 'Related website(s)/service(s)'),
    ('rod', 'Reporting obligation(s) (ROD)'),
    ('stat', 'Statistics')
)

# Organisations vocabulary
class Organisations:
    """ Return organisations as vocabulary
    """
    __implements__ = (IVocabulary,)

    def getDisplayList(self, instance):
        """ Returns vocabulary
        """
        organisations = []
        cat = getToolByName(instance, 'portal_catalog')
        res = cat.searchResults({'portal_type' : 'Organisation'})

        organisations.extend((brain.Title, brain.getUrl)
                             for brain in res)
        #organisations.extend((brain.getUrl, brain.Title)
        #                     for brain in res)
        #return sorted(organisations, key=operator.itemgetter(1))
        organisations.sort()
        return organisations

    def getVocabularyDict(self, instance):
        return {}

    def isFlat(self):
        return False

    def showLeafsOnly(self):
        return False

class OrganisationsVocabularyFactory(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        if hasattr(context, 'context'):
            context = context.context
        data = Organisations().getDisplayList(context)
        return SimpleVocabulary.fromItems(data)

OrganisationsVocabulary = OrganisationsVocabularyFactory()

# Obligations vocabulary
def formatTitle(title):
    res = title
    if len(title) > 80:
        res = title[:80]
        res += ' ...'
    return res

class Obligations:
    """ Return obligations as vocabulary
    """
    __implements__ = (IVocabulary,)

    def getDisplayList(self, instance):
        """ Returns vocabulary
        """
        res = []
        try:
            server = xmlrpclib.Server(ROD_SERVER)
            result = server.WebRODService.getActivities()
        except:
            result = []
        if result:
            res.extend((formatTitle(obligation['TITLE']), int(obligation['PK_RA_ID']))
                        for obligation in result)
        return sorted(res, key=operator.itemgetter(1))

    def getVocabularyDict(self, instance):
        return {}

    def isFlat(self):
        return False

    def showLeafsOnly(self):
        return False

class ObligationsVocabularyFactory(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        if hasattr(context, 'context'):
            context = context.context
        data = Obligations().getDisplayList(context)
        return SimpleVocabulary.fromItems(data)

ObligationsVocabulary = ObligationsVocabularyFactory()

# Geographical coverage vocabulary
COUNTRIES_DICTIONARY_ID = 'european_countries'
def getCountriesDictionary():
    res = {}

    #european countries
    data = getCountries()
    for key in data.keys():
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
    """ return European countries """
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
        #'cs':'cs', #Serbia and Montenegro
        'cy':'cy',
        'cz':'cz',
        'de':'de',
        'dk':'dk',
        'ee':'ee',
        'es':'es',
        'fi':'fi',
        #'fo':'fo', #Faroe Islands
        'fr':'fr',
        'gb':'gb',
        'ge':'ge',
        'gr':'gr',
        'hr':'hr',
        'hu':'hu',
        'ie':'ie',
        'il':'il',
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

# EEA management plan codes vocabulary
EEA_MPCODE_VOCABULARY = {
'2110': '2009-1.1.1 Air quality SEIS and GMES',
'2111': '2009-1.1.2 Air quality assessments and indicators',
'2112': '2009-1.1.3 Noise SEIS and assessments',
'2113': '2009-1.2.1 Air emissions SEIS and GMES',
'2114': '2009-1.2.2 Air emissions assessments and indicators',
'2115': '2009-1.2.3 EMEP/EEA atmospheric emissions Guidebook & TFEIP support',
'2116': '2009-1.3.1 Biodiversity SEIS and GMES',
'2117': '2009-1.3.2 Biodiversity assessments and indicators',
'2119': '2009-1.4.1 Greenhouse gases SEIS and GMES',
'2120': '2009-1.4.2 Greenhouse gases assessments and indicators',
'2121': '2009-1.4.3 UNFCCC and Climate mitigation post-2012',
'2122': '2009-1.5.1 Freshwater SEIS (WISE)',
'2123': '2009-1.5.2 Freshwater assessments and indicators',
'2125': '2009-1.6.1 Marine SEIS and GMES',
'2126': '2009-1.6.2 Marine assessments and indicators',
'2128': '2009-2.1.1 Climate change impacts SEIS and GMES',
'2129': '2009-2.1.2 Climate change impacts assessments and indicators',
'2130': '2009-2.1.3 Hindcasting climate',
'2155': '2009-2.10.1 Transport SEIS and GMES',
'2156': '2009-2.10.2 Transport assessments and indicators',
'2131': '2009-2.2.1 Adaptation and vulnerability SEIS and GMES',
'2132': '2009-2.2.2 Regional and biome assessments and indicators',
'2133': '2009-2.2.3 Methodologies for vulnerability and adaptation (including Droughts)',
'2134': '2009-2.3.1 Land and ecosystem accounting',
'2135': '2009-2.3.2 Ecosystem capacity building',
'2136': '2009-2.3.3 Ecosystem assessments',
'2217': '2009-2.3.4 Pathfinder',
'2137': '2009-2.4.1 Environment and health SEIS',
'2139': '2009-2.4.2 Environment and health assessments and indicators',
'2140': '2009-2.5.1 Maritime SEIS and GMES',
'2141': '2009-2.5.2 Maritime assessments and indicators',
'2143': '2009-2.6.1 SCP assessments and indicators, including resources and chemicals',
'2144': '2009-2.6.2 Waste assessments and indicators',
'2227': '2009-2.6.3 SCP and waste SEIS',
'2146': '2009-2.7.1 Land use SEIS and GMES ',
'2218': '2009-2.7.2 Land use assessments and indicators',
'2149': '2009-2.8.1 Agriculture/forestry assessments and indicators',
'2152': '2009-2.9.1 Energy assessments and indicators ',
'2153': '2009-2.9.2 Renewables',
'2158': '2009-3.1.1 SOER2010 Part A',
'2159': '2009-3.1.2 SOER2010 Part B',
'2219': '2009-3.1.3 SOER2010 Part C',
'2161': '2009-3.2.1 Mediterranean',
'2220': '2009-3.2.2 Arctic',
'2221': '2009-3.2.3 Other assessments',
'2164': '2009-3.3.1 Late Lessons',
'2222': '2009-3.3.2 Methodologies',
'2229': '2009-3.3.3 Decision-support tools',
'2167': '2009-3.4.1 Ecological tax reform',
'2223': '2009-3.4.2 Prices/externalities',
'2224': '2009-3.4.3 Economic assessments',
'2170': '2009-3.5.1 SEIS forward',
'2225': '2009-3.5.2 Strategic futures assessments and indicators',
'2173': '2009-4.1.1 IT development and maintenance',
'2174': '2009-4.1.2 Data centres and indicator management',
'2175': '2009-4.1.3 Management of thematic services',
'2187': '2009-4.1.4 GMES/GEOSS implementation',
'2226': '2009-4.1.5 SEIS/Inspire implementation',
'2176': '2009-4.2.1 Communications planning',
'2177': '2009-4.2.2 Signals',
'2179': '2009-4.3.1 EU institutions',
'2180': '2009-4.3.2 Media and PR',
'2181': '2009-4.3.3 Public outreach',
'2212': '2009-4.3.4 Public enquiry service',
'2213': '2009-4.3.5 Web content and multimedia',
'2214': '2009-4.3.6 Education',
'2188': '2009-4.3.7 Publication and translations',
'2228': '2009-4.3.8 Editing',
'2216': '2009-4.3.9 Marketing and dissemination',
'2182': '2009-4.4.1 Effectiveness evaluation',
'2082': '2009-5.1.1 Management Board and Bureau',
'2083': '2009-5.1.2 Scientific Committee',
'2084': '2009-5.1.3 Eionet coordination including NFP/Eionet, Balkans and EEA country desk officers',
'2085': '2009-5.1.4 Cooperation with European neighbourhood countries',
'2086': '2009-5.2.1 European networks',
'2087': '2009-5.2.2 EPA Secretariat and networks',
'2088': '2009-5.2.3 Research and academic institutions',
'2089': '2009-5.2.4 International Cooperation',
'2230': '2009-5.2.5 Cooperation with UNEP on environmental change',
'2090': '2009-6.1.1 Strategic planning and management',
'2091': '2009-6.1.2 Line management (Career Development Cycle)',
'2092': '2009-6.1.3 Programme/Group management',
'2093': '2009-6.1.4 General Programme/Group support services (excluding missions and meetings)',
'2094': '2009-6.1.5 Learning and development (training)',
'2095': '2009-6.1.6 Staff Committee',
'2096': '2009-6.1.7 Staff meetings',
'2097': '2009-6.1.8 Internal Communication Services',
'2195': '2009-6.1.9 ETC management and coordination',
'2098': '2009-6.2.1 Environmental management system',
'2099': '2009-6.2.2 Quality management and system documentation',
'2100': '2009-6.2.3 Internal audit and control',
'2101': '2009-6.2.4 Data protection',
'2189': '2009-6.2.5 Facilities management',
'2190': '2009-6.2.6 IT infrastructure and services',
'2215': '2009-6.2.7 Document managment',
'2102': '2009-6.3.1 Personnel management',
'2186': '2009-6.3.2 Recruitment and selection',
'2103': '2009-6.3.3 Resource management',
'2185': '2009-6.3.4 Budget life cycle and finance',
'2106': '2009-6.3.5 Travel service including mission support',
'2109': '2009-6.3.6 Accounting',
'2107': '2009-6.3.7 Legal services and procurement',
'2104': '2009-6.3.8 Administrative systems',
'2060': '2009-6.4.1 Leave',
'2061': '2009-6.4.2 Sick leave',
'1679': '2008-1.1.1 Eionet IT systems and developments',
'1680': '2008-1.1.2 Reportnet services',
'1681': '2008-1.1.3 General IT services and infrastructure',
'1846': '2008-1.1.4 Development of general internal systems',
'1682': '2008-1.2.1 Development of the EEA Data Service',
'1683': '2008-1.2.2 Reference data for the EEA spatial data infrastructure',
'1684': '2008-1.2.3 GIS support and map production',
'1685': '2008-1.2.4 European spatial data infrastructure, Inspire and GMES',
'1686': '2008-1.2.5 European datasets and derived products',
'1687': '2008-1.2.6 Corine land cover update',
'1688': '2008-1.2.7 Integration of Shared Environmental Information System components',
'1689': '2008-1.3.1 Publications',
'1690': '2008-1.3.2 Translation',
'1692': '2008-1.3.3 Web site development (design and technical)',
'1858': '2008-1.3.4 Multilingual glossary',
'1779': '2008-10.1.1 Development of methods, tools and web applications',
'1780': '2008-10.1.2 Comprehensive assessments (5yr etc)',
'1781': '2008-10.1.3 Late lessons',
'1860': '2008-10.1.4 Uncertainty and Precaution in Environment and Health Management',
'1862': '2008-10.1.5 Review and analysis of Market Based Instruments',
'1867': '2008-10.1.6 Signals 2009',
'1782': '2008-10.2.1 Environment and Health',
'1783': '2008-10.3.1 Chemicals',
'1784': '2008-10.4.1 Dissemination on environment technologies and innovation',
'1785': '2008-10.4.2 Knowledge development support to eco-innovation initiatives',
'1786': '2008-11.1.1 Strategic planning and management',
'1787': '2008-11.1.2 Line management',
'1788': '2008-11.1.3 Programme support services (excluding meetings)',
'1789': '2008-11.1.4 Support in mission preparation',
'1790': '2008-11.1.5 Learning and development (training)',
'1791': '2008-11.1.6 Staff Committee',
'1792': '2008-11.1.7 Staff meetings',
'1793': '2008-11.1.8 ETC management',
'1794': '2008-11.2.1 European institutions',
'1795': '2008-11.2.2 International institutions',
'1796': '2008-11.2.3 National and regional relations',
'1797': '2008-11.2.4 Research and academic institutions',
'1798': '2008-11.2.5 Industry',
'1799': '2008-11.2.6 EPA Network',
'1800': '2008-11.3.1 Effectiveness evaluation',
'1801': '2008-11.4.1 Environmental management system',
'1806': '2008-12.1.1 Personnel policy issues',
'1807': '2008-12.1.2 Competitions and recruitment service',
'1808': '2008-12.1.3 Corporate staff administration and support',
'1809': '2008-12.2.1 EEA institutional budget cycle',
'1810': '2008-12.2.2 Resource hearings - Balanced scorecard',
'1812': '2008-12.2.3 Learning and development- training management',
'1813': '2008-12.2.4 Job satisfaction survey',
'1866': '2008-12.2.5 Organisational sustainability indicators (EMAS)',
'1814': '2008-12.3.1 Administrative and management systems',
'1815': '2008-12.3.2 Document Management',
'1816': '2008-12.3.3 Quality management system',
'1817': '2008-12.4.1 Ticketing services and helpdesk (ADS only)',
'1818': '2008-12.4.2 Calculation and payment of travel costs (ADS only)',
'1819': '2008-12.5.1 Financial services',
'1820': '2008-12.5.2 Procurement services',
'1821': '2008-12.6.1 Building management',
'1822': '2008-12.6.2 Reception services',
'1823': '2008-12.6.3 Inventory',
'1824': '2008-12.7.1 Financial Accounting',
'1826': '2008-12.8.1 Legal advice',
'1828': '2008-12.8.2 Internal audit',
'1829': '2008-12.8.3 Data protection',
'1830': '2008-12.9.1 Leave',
'1831': '2008-12.9.2 Sick leave',
'1832': '2008-13.1.1 Management board and bureau',
'1833': '2008-13.1.2 Scientific committee',
'1834': '2008-13.1.3 NFP/Eionet coordination',
'1835': '2008-13.1.4 Balkan cooperation coordination',
'1836': '2008-13.1.5 EEA country desk officers',
'1837': '2008-13.2.1 Communication planning',
'1838': '2008-13.2.2 Editing',
'1839': '2008-13.2.3 Exhibitions & Marketing',
'1840': '2008-13.2.4 Events and visiting groups',
'1841': '2008-13.2.5 Media',
'1842': '2008-13.2.6 Product dissemination',
'1856': '2008-13.2.7 Green communication/Awareness raising',
'1843': '2008-13.3.1 Awareness raising activities and networking',
'1844': '2008-13.3.2 Public enquiries',
'1845': '2008-13.3.3 Internal communication services',
'1849': '2008-13.3.4 Library services',
'1850': '2008-13.4.1 Coordination of web content',
'1851': '2008-13.4.2 Coordination of multi-media productions',
'1852': '2008-13.4.3 Environmental education: web products',
'1696': '2008-2.1.1 Data Centre Climate Change',
'1697': '2008-2.1.2 Data capture � Quality assurance/Quality control',
'1698': '2008-2.2.1 Assessment of progress to the EU Kyoto and burden sharing targets',
'1699': '2008-2.2.2 GHG monitoring, accounting, reporting and review',
'1700': '2008-2.2.3 Emission trading',
'1702': '2008-2.3.1 Climate change impact indicators',
'1703': '2008-2.3.2 Climate change vulnerability and adaptation',
'1704': '2008-2.3.3 Costs of inaction to climate change',
'1705': '2008-2.3.4 Climate change outlooks and scenarios',
'1706': '2008-2.4.1 Assessing progress in environmental integration (energy sector)',
'1707': '2008-2.4.2 Renewable energy',
'1859': '2008-2.4.3 Climate change and transport',
'1708': '2008-3.1.1 Contribution to QA/QC of EU reporting data and Eionet data flows',
'1709': '2008-3.1.2 Streamlining European 2010 Biodiversity Indicators',
'1710': '2008-3.1.3 Data Centre design towards implementation',
'1711': '2008-3.1.4 Support and development of the EC/CHM',
'1712': '2008-3.1.5 Communicating and disseminating Biodiversity to wider audiences',
'1713': '2008-3.2.1 Assessments of Natura 2000 network',
'1714': '2008-3.2.2 Ecological aspects of farmland and rural areas',
'1715': '2008-3.2.3 Forest ecosystems conditions',
'1716': '2008-3.2.4 Economic evaluation of benefits of nature management - a framework',
'1717': '2008-3.2.5 European Ecosystem Assessment',
'1718': '2008-4.1.1 Conceptual implementation of  water data centre � defining data needs',
'1719': '2008-4.1.2 Data capture - QA/QC',
'1720': '2008-4.1.3 WISE',
'1721': '2008-4.2.1 Climate change and water',
'1722': '2008-4.2.2 Integrated Marine Assessments',
'1723': '2008-4.2.3 Black Sea report',
'1853': '2008-4.2.4 UN global Regular assessment of the marine Environment',
'1724': '2008-4.2.5 Aquatic ecosystems',
'1725': '2008-4.2.6 Water resources and use, integrated water management',
'1726': '2008-4.2.7 Indicators',
'1728': '2008-4.3.1 LARA � Linkages between agriculture and water quality',
'1729': '2008-4.3.2 Agriculture and environment/Agri-environment indicators',
'1730': '2008-5.1.1 Defining data needs',
'1731': '2008-5.1.2 Data capture - QA/QC',
'1732': '2008-5.1.3 Air quality and emissions data system',
'1733': '2008-5.1.4 EMEP/CORINAIR Atmospheric Emissions Guidebook',
'1734': '2008-5.2.1 Air pollutant emissions assessments',
'1735': '2008-5.2.2 IPPC Directive and PRTR',
'1736': '2008-5.2.3 Air pollutant emissions indicators and inventories',
'1737': '2008-5.3.1 Air quality assessments',
'1738': '2008-5.3.2 Near real time air quality information (IYN)',
'1739': '2008-5.3.3 Air quality indicators and assessment tools',
'1740': '2008-5.4.1 Assessing progress in environmental integration/TERM',
'1741': '2008-5.4.2 Transport subsidies',
'1742': '2008-5.4.3 Transport emission inventories',
'1743': '2008-6.1.1 European neighbourhood policy',
'1744': '2008-6.1.2 Support to Mediterranean policies',
'1745': '2008-6.1.3 Support to Arctic policies and the Northern Dimension',
'1746': '2008-6.2.1 Joint Activities with International Organisations',
'1747': '2008-6.2.2 Joint Activities with non-EEA member countries and other bodies',
'1748': '2008-7.1.1 Measuring SCP and resource efficiency',
'1749': '2008-7.1.2 Support to Eurostat data centres',
'1751': '2008-7.2.1 Environmental impacts from consumption and production using NAMEA',
'1752': '2008-7.2.2 Private and public consumption',
'1753': '2008-7.2.3 SCP integrated assessments',
'1754': '2008-7.2.4 Analysis of impacts and policies related to transboundary movements of waste',
'1755': '2008-7.2.5 The recycling society and its environmental effects',
'1855': '2008-7.2.6 Greening the EEA canteen within the EEA�s EMAS',
'1756': '2008-7.3.1 Effectiveness of waste policies related to the landfill and other directives',
'1863': '2008-7.3.2 Country fact sheets on waste policies',
'1757': '2008-7.3.3 Country fact sheets on SCP policies',
'1758': '2008-8.1.1 Data centre developments',
'1759': '2008-8.1.2 Links to land use scenario modelling and interactive tools',
'1760': '2008-8.2.1 Ecosystems and land use accounts',
'1761': '2008-8.2.2 Spatial features of hydro-systems',
'1762': '2008-8.2.3 Environmental aspects of EU territorial & cohesion policies',
'1763': '2008-8.2.4 Regional and territorial development of Rural areas',
'1764': '2008-8.2.5 Regional and territorial development of Coastal areas',
'1765': '2008-8.2.6 Regional and territorial development of Urban areas',
'1766': '2008-8.2.7 Regional and territorial development of Mountain areas',
'1767': '2008-8.2.8 Spatial assessment of Soil',
'1768': '2008-8.2.9 Noise mapping and assessments',
'1769': '2008-9.1.1 Regular update of outlook indicators',
'1770': '2008-9.1.2 Developing forward looking elements in the context of SOER2010',
'1772': '2008-9.2.1 Exploring the practice and politics of scenarios',
'1773': '2008-9.2.2 Capacity building in Countries and Regions',
'1865': '2008-9.2.3 Methods and conceptual developments',
'1776': '2008-9.3.1 The pan-European region',
'1775': '2008-9.3.2 Providing a future perspective to spatial and ecosystem assessments',
'1777': '2008-9.3.3 Contribution to the Millennium Ecosystem Assessment process',
'1864': '2008-9.3.4 Contribution to foresight exercises',
'1437': '2007-1.1.1 Eionet IT systems and developments',
'1438': '2007-1.1.2 Reportnet services',
'1588': '2007-1.1.3 General IT services and infrastructure',
'1590': '2007-1.2.1 Development of the EEA Data Service',
'1591': '2007-1.2.2 Reference data for the EEA spatial data infrastructure',
'1592': '2007-1.2.3 GIS support and map production',
'1593': '2007-1.2.4 European spatial data infrastructure, Inspire and GMES',
'1594': '2007-1.2.5 European datasets and derived products',
'1644': '2007-1.2.6 Corine land cover update',
'1645': '2007-1.2.7 Integration of Shared Environmental Information System components',
'1604': '2007-1.3.1 Publications',
'1605': '2007-1.3.2 Translation',
'1606': '2007-1.3.3 Web site and content management',
'1607': '2007-1.3.4 Web site development (design and technical)',
'1608': '2007-1.3.5 The European Environmental Encyclopaedia',
'1609': '2007-1.3.6 Web site kids zone',
'1643': '2007-1.3.7 Multilingual glossary',
'1480': '2007-10.1.1 Belgrade report',
'1481': '2007-10.1.2 Development of methods, tools and web applications',
'1482': '2007-10.1.3 Comprehensive assessments (Signals, 5yr etc)',
'1677': '2007-10.1.4 Late lessons',
'1602': '2007-10.2.1 Environment and Health',
'1603': '2007-10.3.1 Chemicals',
'1486': '2007-10.4.1 Dissemination on environment technologies and innovation',
'1678': '2007-10.4.2 Knowledge development support to eco-innovation initiatives',
'1535': '2007-11.1.1 Strategic planning and management',
'1536': '2007-11.1.2 Line management',
'1537': '2007-11.1.3 Programme support services (excluding meetings)',
'1676': '2007-11.1.4 Support in mission preparation',
'1658': '2007-11.1.5 Development of competencies',
'1538': '2007-11.1.6 Staff Committee',
'1539': '2007-11.1.7 Staff meetings',
'1540': '2007-11.1.8 ETC management',
'1529': '2007-11.2.1 European institutions',
'1530': '2007-11.2.2 International institutions',
'1532': '2007-11.2.3 National and regional relations',
'1531': '2007-11.2.4 Research and academic institutions',
'1657': '2007-11.2.5 Industry',
'1533': '2007-11.2.6 EPA Network',
'1582': '2007-11.3.1 Effectiveness evaluation',
'1583': '2007-11.4.1 Environmental management system',
'1584': '2007-11.4.2 Travel',
'1585': '2007-11.4.3 Energy',
'1586': '2007-11.4.4 Green procurement',
'1587': '2007-11.4.5 Material use and waste',
'1848': '2007-11.4.6 Green tips on the Web',
'1521': '2007-12.1.1 Personnel policy issues',
'1522': '2007-12.1.2 Competitions and recruitment service',
'1523': '2007-12.1.3 Corporate staff administration and support',
'1555': '2007-12.2.1 EEA institutional budget cycle',
'1554': '2007-12.2.2 Resource hearings - Balanced scorecard',
'1557': '2007-12.2.3 Document management',
'1659': '2007-12.2.4 Development of competencies - training management',
'1660': '2007-12.2.5 Job satisfaction survey',
'1559': '2007-12.3.1 Administrative and management systems',
'1561': '2007-12.3.2 Corporate mail',
'1558': '2007-12.3.3 Quality management system',
'1549': '2007-12.4.1 Ticketing services and helpdesk (ADS only)',
'1550': '2007-12.4.2 Calculation and payment of travel costs (ADS only)',
'1551': '2007-12.5.1 Financial services',
'1553': '2007-12.5.2 Procurement services',
'1542': '2007-12.6.1 Building management',
'1544': '2007-12.6.2 Reception services',
'1545': '2007-12.6.3 Inventory',
'1519': '2007-12.7.1 Accounting reporting and quality controls',
'1520': '2007-12.7.2 Payments and general ledger operations',
'1562': '2007-12.8.1 Legal advice',
'1563': '2007-12.8.2 Exceptions and risk register',
'1565': '2007-12.8.4 Internal audit',
'1566': '2007-12.8.5 Data protection',
'1595': '2007-12.9.1 Leave/absence',
'1596': '2007-12.9.2 Sick leave',
'1509': '2007-13.1.1 Management board and bureau',
'1510': '2007-13.1.2 Scientific committee',
'1511': '2007-13.1.3 NFP/Eionet coordination',
'1512': '2007-13.1.4 Balkan cooperation coordination',
'1513': '2007-13.1.5 EEA country desk officers',
'1514': '2007-13.2.1 Communication planning',
'1515': '2007-13.2.2 Editing',
'1516': '2007-13.2.3 Exhibitions & Marketing',
'1517': '2007-13.2.4 Events and visiting groups',
'1518': '2007-13.2.5 Media',
'1655': '2007-13.2.6 Product dissemination',
'1526': '2007-13.3.1 Public enquiries',
'1527': '2007-13.3.2 Library services',
'1528': '2007-13.3.3 Awareness raising activities and  networking',
'1573': '2007-2.1.1 Defining data needs',
'1574': '2007-2.1.2 Data capture - QA/QC',
'1613': '2007-2.2.1 Assessment of progress to the EU Kyoto and burden sharing targets',
'1614': '2007-2.2.2 GHG monitoring, accounting, reporting and review',
'1615': '2007-2.2.3 Emission trading',
'1616': '2007-2.2.4 Climate change and transport',
'1618': '2007-2.3.1 Climate change impact indicators',
'1619': '2007-2.3.2 Climate change vulnerability and adaptation',
'1620': '2007-2.3.3 Costs of inaction to climate change',
'1671': '2007-2.3.4 Climate change outlooks and scenarios',
'1621': '2007-2.4.1 Assessing progress in environmental integration (energy sector)',
'1622': '2007-2.4.2 Renewable energy',
'1637': '2007-3.1.1 Contribution to QA/QC of EU reporting data and Eionet data flows',
'1665': '2007-3.1.2 Streamlining European 2010 Biodiversity Indicators',
'1666': '2007-3.1.3 Data Centre design towards implementation',
'1667': '2007-3.1.4 Support and development of the EC/CHM',
'1668': '2007-3.1.5 Communicating and disseminating Biodiversity to wider audiences',
'1630': '2007-3.2.1 Assessments of Natura 2000 network',
'1631': '2007-3.2.2 Ecological aspects of farmland and rural areas',
'1634': '2007-3.2.3 Forest ecosystems conditions',
'1633': '2007-3.2.4 Economic evaluation of benefits of nature management - a framework',
'1632': '2007-3.2.5 European Ecosystem Assessment',
'1448': '2007-4.1.1 Conceptual implementation of  water data centre � defining data needs',
'1449': '2007-4.1.2 Data capture - QA/QC',
'1450': '2007-4.1.3 WISE',
'1569': '2007-4.2.1 Climate change and water',
'1570': '2007-4.2.2 Pan-European Marine assessments',
'1571': '2007-4.2.3 Black Sea report',
'1572': '2007-4.2.4 Small water bodies � assessment of status and threats',
'1672': '2007-4.2.5 Water resources and use, integrated water management',
'1674': '2007-4.2.6 Indicators',
'1451': '2007-4.3.1 LARA � Linkages between agriculture and water quality',
'1452': '2007-4.3.2 Agriculture and environment/Agri-environment indicators',
'1453': '2007-4.3.3 Cross-compliance and farm advisory systems',
'1577': '2007-5.1.1 Defining data needs',
'1578': '2007-5.1.2 Data capture - QA/QC',
'1579': '2007-5.1.3 Air quality and emissions data system',
'1662': '2007-5.1.4 EMEP/CORINAIR Atmospheric Emissions Guidebook',
'1462': '2007-5.2.1 Air pollutant emissions assessments',
'1463': '2007-5.2.2 IPPC Directive and PRTR',
'1663': '2007-5.2.3 Air pollutant emissions indicators and inventories',
'1580': '2007-5.3.1 Air quality assessments',
'1581': '2007-5.3.2 Near real time air quality information (IYN)',
'1664': '2007-5.3.3 Air quality indicators and assessment tools',
'1464': '2007-5.4.1 Assessing progress in environmental integration/TERM',
'1465': '2007-5.4.2 Transport subsidies',
'1466': '2007-5.4.3 Transport emission inventories',
'1504': '2007-6.1.1 EEA multilateral cooperation with EECCA countries',
'1505': '2007-6.1.2 Support to Mediterranean policies',
'1506': '2007-6.1.3 Support to Arctic policies and the Northern Dimension',
'1507': '2007-6.2.1 Joint Activities with International Organisations',
'1508': '2007-6.2.2 Joint Activities with non-EEA member countries and other bodies',
'1483': '2007-7.1.1 Indicators for waste and resources',
'1484': '2007-7.1.2 Support to the establishment of Eurostat data centres',
'1485': '2007-7.1.3 Measuring resource efficiency and SCP',
'1669': '2007-7.2.1 Environmental impacts of consumption and production using NAMEA',
'1648': '2007-7.2.2 UNEP/EEA report on SCP',
'1650': '2007-7.2.3 SCP integrated assessments',
'1651': '2007-7.2.4 Impacts from transboundary movements of waste',
'1670': '2007-7.2.5 The recycling society and its environmental effects',
'1652': '2007-7.3.1 Evaluation of effectiveness of waste policies related to the landfill Directive',
'1653': '2007-7.3.2 Evaluation of effectiveness of economic instruments for resource use',
'1640': '2007-8.1.1 Data centre developments',
'1641': '2007-8.1.2 Links to land use scenario modelling and interactive tools',
'1439': '2007-8.2.1 Ecosystems and land use accounts',
'1440': '2007-8.2.2 Spatial features of hydro-systems',
'1441': '2007-8.2.3 Environmental aspects of EU territorial & cohesion policies',
'1442': '2007-8.2.4 Regional and territorial development of Rural areas',
'1443': '2007-8.2.5 Regional and territorial development of Coastal areas',
'1444': '2007-8.2.6 Regional and territorial development of Urban areas',
'1445': '2007-8.2.7 Regional and territorial development of Mountain areas',
'1447': '2007-8.2.8 Spatial assessment of Soil',
'1446': '2007-8.2.9 Noise mapping and assessments',
'1610': '2007-9.1.1 Consumption, demographics and waste',
'1611': '2007-9.1.2 Regular update of outlook indicators',
'1612': '2007-9.1.3 Review of modelling tools for SOER 2010 II',
'1473': '2007-9.2.1 Methodological developments guidelines and support to the Scientific Committee',
'1474': '2007-9.2.2 PRELUDE 2 Action',
'1475': '2007-9.2.3 Contribution to scenario developments in Spatial and Biodiversity Assessments (EAE support)',
'1567': '2007-9.3.1 Support to GEO 4- Chapter 9',
'1568': '2007-9.3.2 The pan-European region - contribution to Belgrade',
'1675': '2007-9.3.3 Capacity building in Countries and Regions',
'1216': '2006-1.1.1 Eionet IT systems and developments',
'1217': '2006-1.1.2 Reportnet services',
'1218': '2006-1.1.3 General IT services and infrastructure',
'1321': '2006-1.1.4 Management of ongoing DG-Enterprise IDA projects',
'1219': '2006-1.2.1 Development of the EEA Data Service',
'1220': '2006-1.2.2 Reference data for the EEA spatial data infrastructure',
'1221': '2006-1.2.3 GIS support and map production',
'1273': '2006-1.2.4 European spatial data infrastructure, Inspire and GMES',
'1288': '2006-1.2.5 European datasets and derived products',
'1225': '2006-1.3.1 Publications',
'1226': '2006-1.3.2 Translation',
'1227': '2006-1.3.3 Web site and content management',
'1228': '2006-1.3.4 Web site development (design and technical)',
'1229': '2006-1.3.5 The European Environmental Encyclopaedia',
'1274': '2006-1.3.6 Web site kids zone',
'1289': '2006-10.1.1 Belgrade report',
'1291': '2006-10.1.2 Methodology developments & application',
'1433': '2006-10.1.3 Comprehensive assessments (Signals, 5yr etc)',
'1319': '2006-10.2.1 Environment and Health',
'1318': '2006-10.3.1 Chemicals',
'1311': '2006-10.4.1 Dissemination on environment technologies',
'1312': '2006-10.4.2 Development of eco-innovation indicators',
'1314': '2006-10.4.3 Technology orientated assessments',
'1307': '2006-10.5.1 Integrated assessments',
'1308': '2006-10.5.2 Chemicals and environment & health',
'1309': '2006-10.5.3 Technology & innovation',
'1310': '2006-10.5.4 Research links and dissemination',
'1434': '2006-10.5.5 (Co)production of articles and papers',
'1371': '2006-11.1.1 Strategic planning and management',
'1372': '2006-11.1.2 Line management',
'1373': '2006-11.1.3 Assistant support services (excluding missions and meetings)',
'1374': '2006-11.1.4 Staff Committee',
'1375': '2006-11.1.5 Staff/ Programme meetings',
'1431': '2006-11.1.6 Support in Mission preparation',
'1432': '2006-11.1.7 Support in meeting preparation',
'1376': '2006-11.2.1 European institutions',
'1377': '2006-11.2.2 International institutions',
'1378': '2006-11.2.3 Research and academic institutions',
'1379': '2006-11.2.4 National and regional relations',
'1435': '2006-11.2.5 EPA Network',
'1436': '2006-11.2.6 Agency networks',
'1430': '2006-11.3.1 Effectiveness evaluation',
'1380': '2006-11.4.1 Environmental management system',
'1381': '2006-11.4.2 Travel',
'1382': '2006-11.4.3 Energy',
'1383': '2006-11.4.4 Green procurement',
'1384': '2006-11.4.5 Paper',
'1413': '2006-12.1.1 Personnel policy issues',
'1248': '2006-12.1.2 Competitions and recruitment service',
'1249': '2006-12.1.3 Corporate staff administration and support',
'1421': '2006-12.10.1 Development of competencies, training and conferences',
'1419': '2006-12.11.1 Leave/absence',
'1420': '2006-12.11.2 Sick leave',
'1250': '2006-12.2.1 Development of competencies - training management',
'1252': '2006-12.2.2 Career development cycle coordination',
'1414': '2006-12.2.3 Job satisfaction survey',
'1260': '2006-12.3.1 Planning of resource hearings',
'1261': '2006-12.3.2 EEA institutional budget cycle',
'1415': '2006-12.3.3 Balanced scorecard',
'1416': '2006-12.3.4 Document management',
'1262': '2006-12.4.1 Administrative systems',
'1263': '2006-12.4.2 Management systems',
'1265': '2006-12.4.3 Corporate mail',
'1266': '2006-12.4.4 System support to ECDC',
'1254': '2006-12.5.1 Ticketing services and helpdesk (ADS only)',
'1255': '2006-12.5.2 Calculation and payment of travel costs (ADS only)',
'1257': '2006-12.6.1 Financial services by finance officers',
'1258': '2006-12.6.2 Central finance issues?',
'1259': '2006-12.6.3 Procurement services',
'1246': '2006-12.7.1 Building management',
'1247': '2006-12.7.2 Office facilities and support',
'1411': '2006-12.7.3 Reception services',
'1412': '2006-12.7.4 Inventory',
'1230': '2006-12.8.1 Accounting reporting and quality controls',
'1253': '2006-12.8.2 Payments and general ledger operations',
'1268': '2006-12.9.1 Legal advice',
'1267': '2006-12.9.2 Exceptions and risk register',
'1417': '2006-12.9.3 ETC coordination',
'1269': '2006-12.9.4 Internal audit',
'1428': '2006-12.9.5 Data protection',
'1292': '2006-13.1.1 Management board and bureau',
'1293': '2006-13.1.2 Scientific committee',
'1294': '2006-13.1.3 NFP/Eionet coordination',
'1295': '2006-13.1.4 Balkan cooperation coordination',
'1306': '2006-13.1.5 EEA country desk officers',
'1322': '2006-13.2.1 Communication planning',
'1323': '2006-13.2.2 Editing',
'1324': '2006-13.2.3 Exhibitions & Marketing',
'1325': '2006-13.2.4 Events and visiting groups',
'1326': '2006-13.2.5 Media',
'1656': '2006-13.2.6 Product dissemination',
'1351': '2006-13.3.1 Public enquiries',
'1350': '2006-13.3.2 Library services',
'1352': '2006-13.3.3 Information centre networking activities',
'1339': '2006-2.1.1 Defining data needs',
'1340': '2006-2.1.2 Data capture - QA/QC',
'1367': '2006-2.1.3 GHG inventory data system',
'1422': '2006-2.1.4 Ozone depleting substances',
'1163': '2006-2.2.1 Assessment of progress to the EU Kyoto and burden sharing targets',
'1164': '2006-2.2.2 GHG monitoring, accounting, reporting and review',
'1165': '2006-2.2.3 Emission trading',
'1368': '2006-2.2.4 Climate change and transport',
'1423': '2006-2.2.5 Reporting of ozone depleting substances',
'1166': '2006-2.3.1 Climate change impact indicators',
'1167': '2006-2.3.2 Climate change vulnerability and adaptation',
'1168': '2006-2.3.3 Costs of inaction to climate change',
'1169': '2006-2.4.1 Assessing progress in environmental integration (energy sector)',
'1170': '2006-2.4.2 Renewable energy',
'1175': '2006-2.4.3 Environmental implications of carbon capture and storage',
'1424': '2006-2.5.1 Cooperation and partnerships (non-ETC)',
'1369': '2006-2.5.2 ETC Air and climate change (General and CC issues)',
'1232': '2006-3.1.1 Contribution to QA/QC of EU reporting data and EIONET dataflows',
'1233': '2006-3.1.2 Streamlining European 2010 Biodiversity Indicators and contributions to assessments',
'1234': '2006-3.1.3 Spatial & Ecological aspects of Natura 2000 coherence',
'1343': '2006-3.1.4 Ecological aspects of farmland & rural areas',
'1235': '2006-3.1.5 Forest ecosystem conditions and biodiversity',
'1342': '2006-3.1.6 Economic valuation of ecosystems & biodiversity',
'1236': '2006-3.2.1 ETC/BD management',
'1237': '2006-3.2.2 Established cooperation for  data centre',
'1275': '2006-4.1.1 Defining data needs',
'1276': '2006-4.1.2 Data capture - QA/QC',
'1277': '2006-4.1.3 WISE',
'1278': '2006-4.2.1 Climate change and water',
'1280': '2006-4.2.2 Pan-European Marine assessments',
'1281': '2006-4.2.3 Black Sea report',
'1334': '2006-4.2.4 Indicators',
'1282': '2006-4.3.1 LARA � Linkages between agriculture and water quality',
'1283': '2006-4.3.2 Agriculture and environment/Agri-environment indicators',
'1284': '2006-4.3.3 Cross-compliance and farm advisory systems',
'1285': '2006-4.4.1 ETC Water',
'1286': '2006-4.4.2 General support to WFD and marine strategy',
'1333': '2006-4.4.3 Flood risk mapping',
'1287': '2006-4.4.4 JRC, ESTAT, DG AGRI, WMO etc.',
'1337': '2006-5.1.1 Defining data needs',
'1338': '2006-5.1.2 Data capture - QA/QC',
'1366': '2006-5.1.3 Air quality and emissions data system',
'1177': '2006-5.2.1 Air pollutant emissions',
'1178': '2006-5.2.2 IPPC Directive evaluation support',
'1336': '2006-5.3.1 Air quality',
'1335': '2006-5.3.2 Near real time air quality information (IYN)',
'1179': '2006-5.4.1 Assessing progress in environmental integration/TERM',
'1180': '2006-5.4.2 Transport subsidies',
'1181': '2006-5.4.3 Transport emission inventories',
'1425': '2006-5.5.1 Cooperation and partnerships (non-ETC)',
'1370': '2006-5.5.2 ETC Air and climate change (air-related issues)',
'1330': '2006-6.1.1 EEA multilateral cooperation with EECCA countries',
'1331': '2006-6.1.2 Support to Mediterranean policies',
'1332': '2006-6.1.3 Support to Arctic policies and the Northern Dimension',
'1328': '2006-6.2.1 Cooperation and partnerships with international organisations',
'1329': '2006-6.2.2 Cooperation and partnerships with non-European countries and other bodies',
'1315': '2006-7.1.1 Resources & waste indicators',
'1316': '2006-7.1.2 Environmental Impacts of Resource Use & Waste',
'1317': '2006-7.1.3 Policy Assessments of Consumption, Production, Resources & Waste',
'1427': '2006-7.2.1 ETC/RWM management',
'1426': '2006-7.2.2 Cooperation and partnerships non-ETC/RWM',
'1238': '2006-8.1.1 Assessment of Land-based resources by modelling and accounting',
'1239': '2006-8.1.2 Framework of land based environmental resource accounting',
'1344': '2006-8.1.3 Links with scenarios & functional mapping',
'1240': '2006-8.2.1 Producing ecosystems and land use accounts & land use analysis',
'1241': '2006-8.2.2 Producing spacial assessment and accounts of hydro-systems',
'1242': '2006-8.2.3 Territorial cohesion - analysis of environmental aspects of cohesion policy',
'1243': '2006-8.2.4 Regional and territorial development of Rural areas',
'1345': '2006-8.2.5 Regional and territorial development of Coastal areas',
'1346': '2006-8.2.6 Regional and territorial development of Urban areas',
'1347': '2006-8.2.7 Spatial assessment of Soil',
'1348': '2006-8.2.8 Noise mapping',
'1349': '2006-8.2.9 Content & function design of Environment Interactive Atlas',
'1244': '2006-8.3.1 ETC/TE management',
'1245': '2006-8.3.2 Established cooperation for data centre',
'1357': '2006-9.1.1 Outlooks 2005 - evaluation and dissemination of results',
'1358': '2006-9.1.2 Waste outlooks - expanding on previous work',
'1359': '2006-9.1.3 Modelling tools for SoEOR 2010 -  a scoping study',
'1360': '2006-9.2.1 Scenarios of environmental change',
'1361': '2006-9.2.2 PRELUDE 2 Action',
'1429': '2006-9.2.3 Demographics, resources and financial system: a green, long term perspective',
'1362': '2006-9.3.1 Contribution to UNEP Global Environmental Outlooks',
'1363': '2006-9.3.2 Contribution to pan-European assessments',
'1364': '2006-9.4.1 Capacity building in EEA member countries',
'1365': '2006-9.4.2 Cooperation with other international organizations and assessments'}

