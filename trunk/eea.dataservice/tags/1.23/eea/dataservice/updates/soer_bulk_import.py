# -*- coding: utf-8 -*-

""" Bulk import of SOER figures - first batch, see #3987 for more details
"""

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'
__credits__ = """contributions: Alec Ghica"""

from eea.dataservice.updates.soer_bulk_import_data import soer_data
from eea.themecentre.interfaces import IThemeTagging
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
import transaction

# Logging
import logging
logger = logging.getLogger('eea.dataservice')
info = logger.info
info_exception = logger.exception

# Configuration
IMPORT_PATH = "SITE/sandbox/soer-figures"
FILES_PATH = "/var/local/soer_files/FINAL_FIGURES"

# Mappings
THEME_MAPPING = {
    'agriculture':                  'agriculture',
    'air pollution':                'air',
    'biodiversity':                 'biodiversity',
    'climate change':               'climate',
    'coasts and seas':              'coast_sea',
    'energy':                       'energy',
    'environment and health':       'human',
    'environmental technology':     'technology',
    'household consumption':        'households',
    'industry':                     'industry',
    'natural resources':            'natural',
    'tourism':                      'tourism',
    'transport':                    'transport',
    'waste and material resources': 'waste',
    'water':                        'water',
}

def setHtmlMimetype(data):
    if data:
        if not '</' in data:
            if not data.startswith('<p'):
                data = '<p>%s</p>' % data
    return data

# SOER data import
class BulkImportSoerFigures(BrowserView):
    """ Bulk import of SOER figures """

    import_steps = """
    1. [done] export metadata in JSON
    2. [-] import from XML
        1. [-] import EEAFigures
        2. [-] import EEAFigureFiles
        3. [-] extra mappings
        4. [done] transactional import
        5. [-] check encoding during import, e.g. José Barredo
        6. [-] after import owner should not be "alec" but "Carlsten"
    3. [-] generate import logs ( includin mandatory fields warnings )
    4. [-] run a full test on unicorn (including files)
    """

    questions = """
    1. what state should have imported figures and files?
    """

    def __call__(self):
        current_parent = None
        import_context = self.context.unrestrictedTraverse(IMPORT_PATH)
        counter = 0
        
        # countries data
        countriesView = getMultiAdapter((self.context, self.request), name=u'getCountries')
        countries = countriesView()
        countryGroupsView = getMultiAdapter((self.context, self.request), name=u'getCountryGroups')
        countryGroups = countryGroupsView()
        getCountriesByGroupView = getMultiAdapter((self.context, self.request), name=u'getCountriesByGroup')

        for row in soer_data['rows'][:2]:
            counter += 1
            data_dict = {}

            additional_information = row["Additional information"]
            category = row["Category"]
            contact = row["Contact person(s) for EEA"]
            contributors = row["Contributors"]
            copyrights = row["Copyrights"]
            creators = row["Creators"]
            description = row["Description"]
            eea_management_plan = row["EEA Management Plan"]
            figure_type = row["Figure type"]
            filepath = row["Filepath"]
            geo_coverage = row["Geographical coverage"]
            keywords = row["Keywords"]
            last_upload = row["Last upload"]
            methodology = row["Methodology"]
            object_type = row["Object type"]
            owner = row["Owner"]
            processor = row["Processor"]
            source = row["Source"]
            themes = row["Themes"]
            tem_coverage = row["Temporal coverage"]
            title = row["Title"]
            unit = row["Unit"]

            # General metadata
            data_dict['description'] = description
            data_dict['creators'] = creators
            data_dict['rights'] = copyrights

            try:
                if object_type == 'EEAFigure':
                    info('INFO: adding EEAFigure %s' % filepath)

                    fig_id = import_context.invokeFactory(
                              type_name='EEAFigure',
                              id=import_context.generateUniqueId("EEAFigure"))
                    fig_ob = getattr(import_context, fig_id)

                    # Setting EEAFigures metadata
                    data_dict['subject_existing_keywords'] = \
                             [kword.strip() for kword in keywords.split(',')]

                    if not figure_type:
                        figure_type = 'Map'
                    data_dict['figureType'] = figure_type

                    picked_themes = []
                    themes = [th.strip().lower() for th in themes.split(',')]
                    tagging = IThemeTagging(fig_ob)
                    if len(themes) > 3:
                        info('ERROR: more then 3 themes')
                    for theme in themes:
                        th_name = THEME_MAPPING.get(theme, None)
                        if th_name:
                            picked_themes.append(th_name)
                        else:
                            info('ERROR: %s theme not mapped', theme)
                    tagging.tags = picked_themes[:3] #pick first 3 themes

                    data_dict['units'] = setHtmlMimetype(unit)
                    data_dict['methodology'] = setHtmlMimetype(methodology)
                    data_dict['moreInfo'] = \
                             setHtmlMimetype(additional_information)
                    data_dict['dataSource'] = setHtmlMimetype(source)
                    data_dict['contact'] = contact

                    if last_upload:
                        data_dict['lastUpload'] = DateTime(last_upload)
                    #else:
                    #    data_dict['lastUpload'] = DateTime('0000-00-00')

                    picked_plan = ('', '')
                    if eea_management_plan:
                        plan = eea_management_plan.split(',')
                        if len(plan) == 2:
                            picked_plan = (plan[0].strip(), plan[1].strip())
                        elif len(plan) == 1:
                            picked_plan = (plan[0].strip(), '')
                    data_dict['eeaManagementPlan'] = picked_plan

                    picked_temp = []
                    if tem_coverage:
                        for tmp in tem_coverage.split(','):
                            tmp = tmp.strip()
                            if '-' in tmp:
                                tmp_range = range(int(tmp.split('-')[0]),
                                                  int(tmp.split('-')[1]))
                                for trange in tmp_range:
                                    picked_temp.extend(str(trange))
                            elif '–' in tmp:
                                tmp_range = range(int(tmp.split('–')[0]),
                                                  int(tmp.split('–')[1]))
                                for trange in tmp_range:
                                    picked_temp.extend(str(trange))
                            else:
                                picked_temp.append(tmp)
                    data_dict['temporalCoverage'] = picked_temp
                    
                    picked_geo = []
                    for geo in geo_coverage.split(','):
                	geo = geo.strip()
                	countryCode = None
                	for country in countries:
                	    if country[1] == geo:
                		countryCode = [country[0]]
                		break
                	if not countryCode:
                	    for countryGroup in countryGroups:
                		if countryGroup == geo:
                		    countryCode = getCountriesByGroupView(geo)
                		    break
                	if countryCode:
                	    picked_geo.extend(countryCode)
                	else:
                	    info('ERROR: undefined country %s', geo)
            	    data_dict['geographicCoverage'] = picked_geo                  

                    ##data_dict['dataOwner'] = owner
                    
                    # - get URL and/or Title
                    # - check if organisation already exist
                    # - add organisation if not exist
                    
                    #TODO: processor data in current dump is wrong
                    #data_dict['processor'] = processor

                    fig_ob.setTitle(title)
                    fig_ob.processForm(data=1, metadata=1, values=data_dict)
                    fig_ob.reindexObject()

                    current_parent = fig_ob
                    error_detected = False
                elif object_type == 'EEAFigureFile':
                    if current_parent:
                        info('INFO: adding EEAFigureFile %s' % filepath)

                        #data_dict['filepath'] = filepath
                        data_dict['category'] = category

                        #TODO: add EEAFigureFile
                        #TODO: convert images if case
                        pass
                    else:
                        info('ERROR: EEAFigureFile not added %s', filepath)

                else:
                    info('ERROR: unknown "Object type" on %s', filepath)
            except Exception, err:
                if object_type == 'EEAFigure':
                    current_parent = None
                info('ERROR: import error on %s', filepath)
                info_exception(err)

            if counter % 10 == 0:
                info('INFO: Transaction commited, step %s' % str(counter))
                transaction.commit()

        info('INFO: Done soer figures import!')
        return "Done soer figures import!"







