# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

from parser import MigrationObject

def getOrganisationsData():
    """ Returns organisations data
    """
    res = {}
    for key in ORGANISATIONS_DATA.keys():
        data = ORGANISATIONS_DATA[key]
        res[key] = MigrationObject()
        for prop in data.keys():
            res[key].set(prop, data[prop])
    return res

ORGANISATIONS_DATA = {
'EEA': {
    'id': 'EEA',
    'title': 'European Environment Agency',
    'description': 'Data sets used in its periodical reports. The data sets contain aggregated data, typically on a country level, with geographical coverage of at least the 15 EU Member States.',
    'organisationUrl': 'http://www.eea.europa.eu',
    'location': 'Kongens Nytorv 6, 1050, Copenhagen, Denmark',
    'address': 'Kongens Nytorv 6, 1050, Copenhagen, Denmark',
    'data_policy': ''
},
'ETC-ACC': {
    'id': 'ETC-ACC',
    'title': 'The European Topic Centre on Air and Climate Change',
    'description': 'The ETC/ACC supports the EEA in all its tasks relating to air and climate change issues.',
    'organisationUrl': 'http://air-climate.eionet.europa.eu',
    'location': '',
    'data_policy': ''
},
'ETC-LUSI': {
    'id': 'ETC-LUSI',
    'title': 'The European Topic Centre on Land Use and Spatial Information',
    'description': 'The ETC/LUSI supports the EEA in its work of collecting, analysing, evaluating and synthesising information relevant to national and international policies for the environment and for sustainable development.',
    'organisationUrl': 'http://terrestrial.eionet.europa.eu',
    'location': '',
    'data_policy': ''
},
'ETC-NPB': {
    'id': 'ETC-NPB',
    'title': 'The European Topic Centre on Nature Protection and Biodiversity',
    'description': 'The ETC/NPB supports the EEA in its work of collecting, analysing, evaluating and synthesising information relevant to national and international policies for the environment and for sustainable development.',
    'organisationUrl': 'http://biodiversity.eionet.europa.eu',
    'location': '',
    'data_policy': ''
},
'ETC-WTR': {
    'id': 'ETC-WTR',
    'title': 'The European Topic Centre on Water',
    'description': 'The ETC/WTR is an international consortium brought together to support the EEA in its mission to deliver timely, targeted, relevant and reliable information to policy-makers and the public for the development and implementation of sound environmental policies in the European Union and other EEA member countries.',
    'organisationUrl': 'http://water.eionet.europa.eu',
    'location': '',
    'data_policy': ''
},
'FMA': {
    'id': 'FMA',
    'title': 'Applied Meteorology Foundation (FMA)',
    'description': 'Applied Meteorology Foundation (FMA)',
    'organisationUrl': 'http://www.ibimet.cnr.it/programmi/Pcase/index.htm',
    'location': '',
    'data_policy': ''
},
'BL': {
    'id': 'BLF',
    'title': 'BirdLife',
    'description': "BirdLife International is a global alliance of conservation organisations working together for the world's birds and people",
    'organisationUrl': 'http://www.birdlife.net',
    'location': '',
    'data_policy': ''
},
'CE': {
    'id': 'CE',
    'title': 'Council of Europe',
    'description': "The Council of Europe launched its environment programme in 1961, to deal with one of the issues now perceived as one of the main challenges that Europe will have to face in the 21st century. The Council of Europe's activities in this field focus on the conservation of nature and landscapes.",
    'organisationUrl': 'http://www.coe.int',
    'location': '',
    'data_policy': ''
},
'DEFA': {
    'id': 'DEFA',
    'title': 'Directorate-general for Economic and Financial Affairs',
    'description': 'This is where you find information about economic and financial issues in the European Union',
    'organisationUrl': 'http://ec.europa.eu/economy_finance/index_en.htm',
    'location': '',
    'data_policy': ''
},
'DIS-MED': {
    'id': 'DIS-MED',
    'title': 'Desertification Information System for the Mediterranean',
    'description': 'The objective of the DIS/MED project is to improve the capacity of national administrations in the Mediterranean countries to effectively programme measures and policies to combat desertification and the effects of drought.',
    'organisationUrl': 'http://dismed.eionet.europa.eu',
    'location': '',
    'data_policy': ''
},
'WCU': {
    'id': 'WCU',
    'title': 'The World Conservation Union',
    'description': 'The World Conservation Union is the world’s largest and most important conservation network. The Union brings together 82 States, 111 government agencies, more than 800 non-governmental organizations (NGOs), and some 10,000 scientists and experts from 181 countries in a unique worldwide partnership.',
    'organisationUrl': 'http://www.iucn.org',
    'location': '',
    'data_policy': ''
},
'DGE': {
    'id': 'DGE',
    'title': 'Directorate-general for Environment',
    'description': 'Environmental statistics compiled by the DG Environment ',
    'organisationUrl': 'http://ec.europa.eu/dgs/environment/index_en.htm',
    'location': '',
    'data_policy': ''
},
'EBCC': {
    'id': 'EBCC',
    'title': 'European Bird Census Council',
    'description': 'EBCC',
    'organisationUrl': 'http://www.ebcc.info',
    'location': '',
    'data_policy': ''
},
'IGCRM': {
    'id': 'IGCRM',
    'title': 'Institute of Geodesy, Cartography and Remote Sensing',
    'description': 'The Institute of Geodesy, Cartography and Remote Sensing (FÖMI) has been founded in 1967. The Institute is the central surveying and mapping organisation of all official activities in Hungary in the field of land management, surveying and mapping. It is financed by the state budget and has the competence of a national authority. Its direct professional supervisory authority is the Ministry of Agriculture and Rural Development, Department of Land Administration and Geoinformation.',
    'organisationUrl': 'http://www.fomi.hu/honlap/angol/Default.htm',
    'location': '',
    'data_policy': ''
},
'NGDC': {
    'id': 'NGDC',
    'title': "NOAA's National Geophysical Data Center (NGDC)",
    'description': "NOAA's National Geophysical Data Center (NGDC) provides scientific stewardship, products, and services for geophysical data describing the sea floor, solid earth, and solar-terrestrial environment, including Earth observations from space. ",
    'organisationUrl': 'http://www.ngdc.noaa.gov',
    'location': '',
    'data_policy': ''
},
'ICES': {
    'id': 'ICES',
    'title': 'International Council for the Exploration of the Sea',
    'description': 'Marine ecosystem statistics compiled by the ICES',
    'organisationUrl': 'http://www.ices.dk',
    'location': 'Palægade 2-4, DK - 1261, Copenhagen, Denmark',
    'address': 'Palægade 2-4, DK - 1261, Copenhagen, Denmark',
    'data_policy': ''
},
'RSPB': {
    'id': 'RSPB',
    'title': 'Royal Society for the Protection of Birds',
    'description': 'The RSPB is the UK charity working to secure a healthy environment for birds and wildlife, helping to create a better world for us all.',
    'organisationUrl': 'http://www.rspb.org.uk',
    'location': '',
    'data_policy': ''
},
'SOEC': {
    'id': 'SOEC',
    'title': 'Statistical Office of the European Communities',
    'description': 'The key role of Eurostat is to supply statistical data to the Commission and other European Institutions so they can define, implement and analyse Community policies. ',
    'organisationUrl': 'http://epp.eurostat.ec.europa.eu',
    'location': 'Bâtiment Jean Monnet Rue Alcide de Gasperi, L-2920, Luxembourg, Luxembourg',
    'address': 'Bâtiment Jean Monnet Rue Alcide de Gasperi, L-2920, Luxembourg, Luxembourg',
    'data_policy': ''
},
'STAN': {
    'id': 'STAN',
    'title': 'Statistics Netherlands',
    'description': 'Statistics Netherlands is responsible for collecting, processing and publishing statistics to be used in practice, by policymakers and for scientific research. In addition to its responsibility for (official) national statistics, Statistics Netherlands also has the task of producing European (community) statistics. The legal basis for Statistics Netherlands and its work is the Act of 20 November 2003 governing the central bureau of statistics (Statistics Netherlands).',
    'organisationUrl': 'http://www.cbs.nl/en-GB/default.htm',
    'location': '',
    'data_policy': ''
},
'FAO': {
    'id': 'FAO',
    'title': 'The Food and Agriculture Organisation',
    'description': 'The Food and Agriculture Organization of the United Nations leads international efforts to defeat hunger. Serving both developed and developing countries, FAO acts as a neutral forum where all nations meet as equals to negotiate agreements and debate policy. FAO is also a source of knowledge and information.',
    'organisationUrl': 'http://www.fao.org/',
    'location': 'Viale delle Terme di Caracalla, 00100, Rome, Italy',
    'address': 'Viale delle Terme di Caracalla, 00100, Rome, Italy',
    'data_policy': ''
},
'JRC': {
    'id': 'JRC',
    'title': 'The Joint Research Centre',
    'description': 'The Joint Research Centre is the scientific and technical research laboratory of the European Union and part of the European Commission. It is a directorate-general, and provides scientific advice and the technical know-how for supporting EU policies. Its status as a Commission service, which guarantees its independence from private and national interests, is crucial for pursuing its mission.',
    'organisationUrl': 'http://www.jrc.it',
    'location': 'Joint Research Centre, Institute for Environment and Sustainability, TP 262, 21020 Ispra (VA), Italy',
    'address': 'Joint Research Centre, Institute for Environment and Sustainability, TP 262, 21020 Ispra (VA), Italy',
    'data_policy': ''
},
'UNECE': {
    'id': 'UNECE',
    'title': 'The United Nations Economic Commission for Europe (Environment and Human Settlements Division)',
    'description': 'UNECE Environment and Human Settlements Division.',
    'organisationUrl': 'http://www.unece.org/env',
    'location': '',
    'data_policy': ''
},
'UNEP': {
    'id': 'UNEP',
    'title': 'The United Nations Environment Programme',
    'description': 'Statistics compiled by the United Nations Environment Programme ',
    'organisationUrl': 'http://www.unep.org',
    'location': '',
    'data_policy': ''
},
'ABER': {
    'id': 'ABER',
    'title': 'The University of Wales, Aberystwyth',
    'description': 'Founded in 1872, Aberystwyth was the first university to be established in Wales. It aims to fulfil its special responsibility for the educational needs of Wales, and to maintain and develop partnerships with industry and other institutions both within Wales and beyond, and also to promote collaboration in teaching and research between the constituent parts of the University of Wales.',
    'organisationUrl': 'http://www.aber.ac.uk',
    'location': '',
    'data_policy': ''
},
'UNEP-WCMC': {
    'id': 'UNEP-WCMC',
    'title': 'United Nations Environment Programme World Conservation Monitoring Centre',
    'description': 'The UNEP World Conservation Monitoring Centre provides information for policy and action to conserve the living world.',
    'organisationUrl': 'http://www.unep-wcmc.org',
    'location': '',
    'data_policy': ''
},
'UNFCCC': {
    'id': 'UNFCCC',
    'title': 'United Nations Framework Convention on Climate Change',
    'description': 'The main functions of the secretariat of the UNFCC are to make practical arrangements for sessions of the Convention bodies, to assist Parties in implementing their commitments, to provide support to on-going negotiations and to coordinate with the secretariats of other relevant international bodies, notably the Global Environment Facility (GEF) and its implementing agencies (UNDP, UNEP and the World Bank), the Intergovernmental Panel on Climate Change (IPCC), and other relevant conventions.',
    'organisationUrl': 'http://www.unfccc.int',
    'location': '',
    'data_policy': ''
}
}