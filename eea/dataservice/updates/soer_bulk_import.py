# -*- coding: utf-8 -*-

""" Bulk import of SOER figures - first batch, see #3987 for more details
"""

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'
__credits__ = """contributions: Alec Ghica"""

from DateTime import DateTime
from eea.dataservice.updates.soer_bulk_import_data import soer_data
from eea.themecentre.interfaces import IThemeTagging
import os
import os.path
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from StringIO import StringIO
import transaction
from zope.component import getMultiAdapter

# Logging
import logging
logger = logging.getLogger('eea.dataservice')
info = logger.info
info_exception = logger.exception

# Configuration
IMPORT_PATH = "SITE/sandbox/soer-figures"
FILES_PATH = "/var/eeawebtest/soer_files"

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

CATEGORY_MAPPING = {
    'Hard copy':   'hard',
    'Methodology': 'meto',
}

PUBLICATIONS_MAPPING = {
    ('soer2010', 'thematic assessment', 'air pollution'):
        'SITE/soer/europe/air-pollution',
    ('soer2010', 'thematic assessment', 'nature and biodiversity'):
        'SITE/soer/europe/biodiversity',
    ('soer2010', 'thematic assessment', 'climate change',
     'understanding climate change'):
        'SITE/soer/europe/understanding-climate-change',
    ('soer2010', 'thematic assessment', 'climate change', 'mitigation'):
        'SITE/soer/europe/mitigating-climate-change',
    ('soer2010', 'thematic assessment', 'climate change', 'adaptation'):
        'SITE/soer/europe/adapting-to-climate-change',
    ('soer2010', 'thematic assessment', 'land use'):
        'SITE/soer/europe/land-use',
    ('soer2010', 'thematic assessment', 'soil'):
        'SITE/soer/europe/soil',
    ('soer2010', 'thematic assessment', 'marine and coastal'):
        'SITE/soer/europe/marine-and-coastal-environment',
    ('soer2010', 'thematic assessment', 'consumption'):
        'SITE/soer/europe/consumption-and-environment',
    ('soer2010', 'thematic assessment', 'material resources', 'waste'):
        'SITE/soer/europe/material-resources-and-waste',
    ('soer2010', 'thematic assessment', 'urban environment'):
        'SITE/soer/europe/urban-environment',
    ('soer2010', 'thematic assessment', 'freshwater quality'):
        'SITE/soer/europe/freshwater-quality',
    ('soer2010', 'thematic assessment', 'water resources'):
        'SITE/soer/europe/water-resources-quantity-and-flows',
}

#TODO: add files mapping, related to "megatrends" keyword, used for next batch

# Utils
def setHtmlMimetype(data):
    """ set mimetype to HTML """
    if data:
        if not '</' in data:
            if not data.startswith('<p'):
                data = '<p>%s</p>' % data
    return data

def validateExternalURL(url, context, request):
    """ check external URLs """
    status = True
    if not url.startswith('http://'):
        info('ERROR: URL ( %s ) validation: bad format', url)
        status = False
        return status

    LinkChecker = getMultiAdapter((context, request),
                                   name=u'migration_link_checker')
    status_code = LinkChecker.getStatusCode(url)
    status_msg = LinkChecker.getStatusMsg(status_code)
    if status_code in [110, 404]:
        info('ERROR: status code %s ::: %s', status_code, url)
        status = False
    return status

def checkOrganisation(context, url, title=''):
    """ Check if an Organisation pointing to this URL
        already exists, if not add a new one
    """
    # Check if an Organisation already exists
    ctool = getToolByName(context, 'portal_catalog')
    query = { 'portal_type': ['Organisation'],
              'getUrl': url }
    brains = ctool(**query)

    if brains:
        info('INFO: Organisation found.')
    else:
        # There is no Organisation pointing to our URL, create a new one
        info('INFO: Adding organisation :: %s', url)
        org_path = 'SITE/data-and-maps/data-providers-and-partners'
        org_container = context.unrestrictedTraverse(org_path)

        org_id = org_container.invokeFactory('Organisation',
                                             id="new_organisation")
        org_ob = org_container._getOb(org_id)

        # Set metadata
        if not title:
            title = url
        org_ob.setTitle(title)

        datamodel = {}
        datamodel['organisationUrl'] = url
        org_ob.processForm(data=1, metadata=1, values=datamodel)
        # Set workflow state
        wftool = getToolByName(context, 'portal_workflow')
        state = wftool.getInfoFor(org_ob, 'review_state', '(Unknown)')
        if state == 'published':
            return
        try:
            wftool.doActionFor(org_ob, 'publish',
                               comment='Set by SOER2010 bulk import script.')
        except Exception, err:
            info('ERROR: setting workflow')
            #info_exception('Exception: %s ', err)

        org_ob.reindexObject()
        info('INFO: Organisation update done')

def changeOwnership(context, membertool, username, workflow_id):
    """ change ownership and workflow history """

    # Change ownership
    user_ob = membertool.getMemberById(username)
    context.changeOwnership(user=user_ob, recursive=1)

    # Set 'owner' role
    owners = context.users_with_local_role('Owner')
    for o in owners:
        context.manage_delLocalRoles([o])
    context.manage_setLocalRoles(username, ['Owner'])
    context.reindexObjectSecurity()
    #try:
        #context.folder_localrole_edit('add',
                                       #member_ids=tuple(username),
                                       #member_role=['Owner'])
        #context.folder_localrole_set(use_acquisition=0)
    #except Exception, err:
        #info('ERROR: error setting local role')
        #info_exception('Exception: %s ', err)

    ## Update workflow history
    #wf_state = {
        #'action': 'Ownership changed',
        #'actor': username
        #'comments': "Set by migration script.",
        #'review_state': 'content_pending',
        #'time': DateTime(),
    #}
    #wftool.setStatusOf(workflow_id, context, wf_state)

    # Update workflow history
    history = context.workflow_history[workflow_id]
    history = list(history)
    updated_history = []
    count = 0
    for entry in history:
        entry['actor'] = username
        if count == 0:
            entry['action'] = 'Import of SOER figures'
            entry['comments'] = 'Set by migration script.'
        updated_history.append(entry)
        count += 1
    context.workflow_history[workflow_id] = tuple(updated_history)

def convertEEAFigureFile(context, request):
    """ Convert EEAFigureFiles """
    convert = getMultiAdapter((context, request), name=u'convertMap')
    try:
        error = convert(cronjob=True)
    except:
        info('ERROR: error converting file')

def findRelatedPublications(context, fig_keywords):
    """ returns related publication based on keywords match """
    publication_ob = None
    figure_keywords = [fig.lower() for fig in fig_keywords]

    for keyword_set in PUBLICATIONS_MAPPING.keys():
        key_flag = True
        for keyword in keyword_set:
            if not keyword in figure_keywords:
                key_flag = False
                break
        if key_flag:
            break

    if keyword_set and key_flag:
        publication_ob = context.unrestrictedTraverse(
                                PUBLICATIONS_MAPPING[keyword_set])
    return publication_ob

# SOER data import
class BulkImportSoerFigures(BrowserView):
    """ Bulk import of SOER figures """

    import_errors = """
ERROR: undefined country EEA32
ERROR: undefined country EU12
ERROR: undefined country USA
ERROR: undefined country EFTA
ERROR: undefined country Greenland
    """

    def __call__(self):
        import_context = self.context.unrestrictedTraverse(IMPORT_PATH)
        putils = getToolByName(self.context, 'plone_utils')
        wftool = getToolByName(self.context, 'portal_workflow')
        membertool = getToolByName(self.context, 'portal_membership')
        username = 'iverscar'
        workflow_id = 'eea_data_workflow'
        current_parent = None
        counter = 0

        # countries data
        countriesView = getMultiAdapter((self.context, self.request),
                                         name=u'getCountries')
        countries = countriesView()
        countryGroupsView = getMultiAdapter((self.context, self.request),
                                             name=u'getCountryGroups')
        countryGroups = countryGroupsView()
        getCountriesByGroupView = getMultiAdapter(
            (self.context, self.request),
             name=u'getCountriesByGroup')

        for row in soer_data['rows']:
            data_dict = {}
            all_mandatory = True

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
                    counter += 1
                    info('INFO: adding EEAFigure %s' % filepath)

                    fig_id = import_context.invokeFactory(
                              type_name='EEAFigure',
                              id=import_context.generateUniqueId("EEAFigure"))
                    fig_ob = getattr(import_context, fig_id)

                    # Setting EEAFigures metadata
                    keywords_list = [kword.strip()
                                     for kword in keywords.split(',')]
                    data_dict['subject_existing_keywords'] = keywords_list

                    if not description:
                        info('ERROR: no desription')
                        all_mandatory = False

                    if not figure_type:
                        info('ERROR: no "figure type" defined')
                        all_mandatory = False
                    else:
                        data_dict['figureType'] = figure_type.lower()

                    if not themes:
                        info('ERROR: no theme')
                        all_mandatory = False
                    else:
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
                    if source:
                        data_dict['dataSource'] = setHtmlMimetype(source)
                    else:
                        all_mandatory = False
                    if contact:
                        data_dict['contact'] = contact.replace('\n', '\r\n')
                    else:
                        all_mandatory = False

                    if last_upload:
                        data_dict['lastUpload'] = DateTime(last_upload)
                    else:
                        info('ERROR: no lastUpload')
                        all_mandatory = False
                    #else:
                    #    data_dict['lastUpload'] = DateTime('0000-00-00')

                    picked_plan = ('', '')
                    if eea_management_plan:
                        plan = eea_management_plan.split(',')
                        if len(plan) == 2:
                            picked_plan = (int(plan[0].strip()),
                                           plan[1].strip())
                        elif len(plan) == 1:
                            picked_plan = (int(plan[0].strip()), '')
                    data_dict['eeaManagementPlanYear'] = picked_plan[0]
                    data_dict['eeaManagementPlanCode'] = picked_plan[1]

                    picked_temp = []
                    if tem_coverage:
                        for tmp in tem_coverage.split(','):
                            tmp = tmp.strip()
                            if '-' in tmp:
                                tmp_range = range(int(tmp.split('-')[0]),
                                                  int(tmp.split('-')[1]))
                                for trange in tmp_range:
                                    picked_temp.extend([str(trange)])
                            elif '–' in tmp:
                                tmp_range = range(int(tmp.split('–')[0]),
                                                  int(tmp.split('–')[1]))
                                for trange in tmp_range:
                                    picked_temp.extend([str(trange)])
                            else:
                                picked_temp.append(tmp)
                    if not picked_temp:
                        all_mandatory = False

                    data_dict['temporalCoverage'] = picked_temp

                    picked_geo = []
                    for geo in geo_coverage.split(','):
                        geo = geo.strip()
                        if geo == 'EFTA':
                            geo = 'EFTA4'
                        if geo in ['USA', 'Greenland']:
                            data_dict['subject_existing_keywords'].append(geo)
                            continue
                        countryCode = None
                        for country in countries:
                            if country[1] == geo:
                                countryCode = [country[0]]
                                break
                        if geo == 'Former Yugoslav Republic of Macedonia':
                            countryCode = 'mk'
                        if not countryCode:
                            geo = geo.replace(' ', '')
                            geo = geo.replace('-', '')
                            for countryGroup in countryGroups:
                                if countryGroup == geo:
                                    countryCode = getCountriesByGroupView(geo)
                                    break
                        if countryCode:
                            picked_geo.extend(countryCode)
                        else:
                            info('ERROR: undefined country %s', geo)
                    if not picked_geo:
                        info('ERROR: no geographicCoverage defined')
                        all_mandatory = False
                    data_dict['geographicCoverage'] = picked_geo

                    if owner:
                        owner_data = owner.split(',')
                        if len(owner_data) > 2:
                            info('ERROR: bad format Owner')
                            all_mandatory = False
                        else:
                            owner_url = owner_data[0]
                            owner_title = ''
                            if len(owner_data) == 2:
                                owner_title = owner_data[1]

                            status = validateExternalURL(owner_url,
                                                         self.context,
                                                         self.request)
                            if status:
                                checkOrganisation(self.context,
                                                  owner_url,
                                                  owner_title.strip())
                                data_dict['dataOwner'] = [owner_url]
                            else:
                                all_mandatory = False
                    else:
                        all_mandatory = False

                    #TODO: processor data in current dump is wrong
                    #data_dict['processor'] = processor

                    # Set state to 'content_pending' if not all mandatory
                    # fields were filled in and 'published' otherwise.
                    try:
                        if all_mandatory:
                            wftool.doActionFor(
 fig_ob, 'quickPublish',
 comment='Published by SOER2010 bulk import since all mandatory are present.')
                        else:
                            wftool.doActionFor(
                                fig_ob, 'submitContentReview',
                                comment='Set by SOER2010 bulk import script.')
                    except Exception, err:
                        info('ERROR: setting workflow')
                        #info_exception('Exception: %s ', err)

                    # Change ownership
                    changeOwnership(fig_ob, membertool, username, workflow_id)

                    # Save metadata
                    fig_ob.setTitle(title)
                    fig_ob.processForm(data=1, metadata=1, values=data_dict)

                    publication_ob = findRelatedPublications(self.context,
                                                             keywords_list)
                    if publication_ob:
                        fig_ob.setRelatedProducts([publication_ob])


                    fig_ob.reindexObject()
                    info('INFO: done adding %s', fig_ob.getId())

                    current_parent = fig_ob
                    error_detected = False

                    if filepath:
                        counter += 1
                        eps_data_dict = {}
                        info('INFO: adding EEAFigureFile (EPS) %s' % filepath)

                        if filepath[len(filepath)-4:] != '.eps':
                            filepath = '%s.eps' % filepath

                        file_name = filepath.split('/')[1]
                        file_id = putils.normalizeString(file_name)

                        file_id = current_parent.invokeFactory(
                            'EEAFigureFile',
                            id=file_id)
                        file_ob = getattr(current_parent, file_id)

                        file_path = os.path.join(FILES_PATH, filepath)
                        file_stream = open(file_path, 'rb')
                        file_data = file_stream.read()
                        file_name = file_name.encode('utf-8')
                        fp = StringIO(file_data)
                        fp.filename = file_name
                        file_ob.setFile(fp, _migration_=True)

                        #eps_data_dict['description'] = description
                        eps_data_dict['creators'] = creators
                        eps_data_dict['rights'] = copyrights
                        if category:
                            eps_data_dict['category'] = \
                                         CATEGORY_MAPPING[category]

                        # Set state to 'content_pending'
                        try:
                            wftool.doActionFor(
                                file_ob, 'quickPublish',
                                comment='Set by SOER2010 bulk import script.')
                        except Exception, err:
                            info('ERROR: error setting workflow')
                            #info_exception('Exception: %s ', err)

                        # Change ownership
                        changeOwnership(file_ob,
                                        membertool,
                                        username,
                                        workflow_id)

                        file_ob.processForm(data=1,
                                            metadata=1,
                                            values=eps_data_dict)

                        if not title:
                            title = file_name
                        file_ob.setTitle(title)

                        # Convert image if case
                        convertEEAFigureFile(file_ob, self.request)

                        file_ob.reindexObject()
                        info('INFO: done adding %s', file_ob.getId())
                elif object_type == 'EEAFigureFile':
                    counter += 1
                    if current_parent:
                        info('INFO: adding EEAFigureFile %s' % filepath)

                        file_name = filepath.split('/')[1]
                        file_id = putils.normalizeString(file_name)

                        file_id = current_parent.invokeFactory(
                            'EEAFigureFile',
                            id=file_id)
                        file_ob = getattr(current_parent, file_id)

                        file_path = os.path.join(FILES_PATH, filepath)
                        file_stream = open(file_path, 'rb')
                        file_data = file_stream.read()
                        file_name = file_name.encode('utf-8')
                        fp = StringIO(file_data)
                        fp.filename = file_name
                        file_ob.setFile(fp, _migration_=True)

                        if category:
                            data_dict['category'] = CATEGORY_MAPPING[category]

                        # Set state to 'content_pending'
                        try:
                            wftool.doActionFor(
                                file_ob, 'quickPublish',
                                comment='Set by SOER2010 bulk import script.')
                        except Exception, err:
                            info('ERROR: error setting workflow')
                            #info_exception('Exception: %s ', err)

                        # Change ownership
                        changeOwnership(file_ob,
                                        membertool,
                                        username,
                                        workflow_id)

                        file_ob.processForm(data=1,
                                            metadata=1,
                                            values=data_dict)

                        if not title:
                            title = file_name
                        file_ob.setTitle(title)

                        # Convert image if case
                        convertEEAFigureFile(file_ob, self.request)

                        file_ob.reindexObject()
                        info('INFO: done adding %s', file_ob.getId())
                    else:
                        info('ERROR: EEAFigureFile not added %s', filepath)

                else:
                    info('ERROR: unknown "Object type" on %s', filepath)
            except Exception, err:
                if object_type == 'EEAFigure':
                    current_parent = None
                info('ERROR: import error on %s', filepath)
                info_exception(err)

            info('INFO: objects added %s' % str(counter))
            if counter % 10 == 0:
                info('INFO: Transaction commited, step %s' % str(counter))
                transaction.commit()

        info('INFO: *** Done soer figures import! ***')
        return " *** Done soer figures import! *** "
