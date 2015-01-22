""" Various setup
"""
import logging
from Products.CMFCore.utils import getToolByName
from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL
from Products.ATVocabularyManager.utils.vocabs import createHierarchicalVocabs
from Products.ATVocabularyManager.utils.vocabs import createSimpleVocabs
from eea.dataservice.vocabulary import (
    CATEGORIES_DICTIONARY,
    CATEGORIES_DICTIONARY_ID,
    CONVERSIONS_DICTIONARY,
    CONVERSIONS_DICTIONARY_ID,
    CONVERSIONS_USED,
    COUNTRIES_DICTIONARY_ID,
    getCountriesDictionary,
    QLD_DICTIONARY,
    QLD_DICTIONARY_ID,
    QLMG_DICTIONARY,
    QLMG_DICTIONARY_ID,
    QUALITY_DICTIONARY,
    QUALITY_DICTIONARY_ID,
    REFERENCE_DICTIONARY,
    REFERENCE_DICTIONARY_ID
)
from eea.dataservice.mimetypes.database import MIMETYPES as DB_MIMETYPES
from eea.dataservice.mimetypes.geographic import MIMETYPES as GEO_MIMETYPES
from eea.dataservice.mimetypes.utils import register_mimetypes

logger = logging.getLogger('eea.dataservice: setuphandlers')

def installVocabularies(context):
    """ Creates/imports the atvm vocabs.
    """
    # only run this step if we are in eea.dataservice profile
    if context.readDataFile('eea.dataservice.txt') is None:
        return

    site = context.getSite()
    atvm = getToolByName(site, ATVOCABULARYTOOL)

    # Creat countries vocabulary
    if COUNTRIES_DICTIONARY_ID not in atvm.contentIds():
        hierarchicalVocab = {}
        hierarchicalVocab[(COUNTRIES_DICTIONARY_ID, 'European Countries')] = {}
        createHierarchicalVocabs(atvm, hierarchicalVocab)

        countries = getCountriesDictionary()
        for term in countries.keys():
            vocab = atvm[COUNTRIES_DICTIONARY_ID]
            vocab.invokeFactory('TreeVocabularyTerm', term[0], title=term[1])
            for subterm in countries[term].keys():
                subvocab = vocab[term[0]]
                subvocab.invokeFactory('TreeVocabularyTerm',
                                       subterm[0], title=subterm[1])
                subvocab.reindexObject()
            vocab.reindexObject()
    else:
        logger.warn('eea.dataservice countries vocabulary already exist.')

    # Create reference vocabulary
    if REFERENCE_DICTIONARY_ID not in atvm.contentIds():
        createSimpleVocabs(atvm, REFERENCE_DICTIONARY)
        atvm[REFERENCE_DICTIONARY_ID].setTitle('Coordinate reference system')
    else:
        logger.warn('eea.dataservice reference vocabulary already exist.')

    # Create quality vocabulary
    if QUALITY_DICTIONARY_ID not in atvm.contentIds():
        createSimpleVocabs(atvm, QUALITY_DICTIONARY)
        atvm[QUALITY_DICTIONARY_ID].setTitle('Geographic information quality')
    else:
        logger.warn('eea.dataservice quality vocabulary already exist.')

    # Create quick link vocabulary for datasets
    if QLD_DICTIONARY_ID not in atvm.contentIds():
        createSimpleVocabs(atvm, QLD_DICTIONARY)
        atvm[QLD_DICTIONARY_ID].setTitle('Datasets quick links')
    else:
        logger.warn('eea.dataservice quick link vocabulary for datasets '
                    'already exist.')

    # Create quick link vocabulary for maps and graphs
    if QLMG_DICTIONARY_ID not in atvm.contentIds():
        createSimpleVocabs(atvm, QLMG_DICTIONARY)
        atvm[QLMG_DICTIONARY_ID].setTitle('Maps & graphs quick links')
    else:
        logger.warn('eea.dataservice quick link vocabulary for maps and graphs '
                    'already exist.')

    # Create categories vocabulary
    if CATEGORIES_DICTIONARY_ID not in atvm.contentIds():
        createSimpleVocabs(atvm, CATEGORIES_DICTIONARY)
        atvm[CATEGORIES_DICTIONARY_ID].setTitle('Dataservice categories')
    else:
        logger.warn('eea.dataservice categories vocabulary already exist.')

    # Create conversions vocabulary
    convertion_fresh_install = False
    if CONVERSIONS_DICTIONARY_ID not in atvm.contentIds():
        convertion_fresh_install = True
        createSimpleVocabs(atvm, CONVERSIONS_DICTIONARY)
        atvm[CONVERSIONS_DICTIONARY_ID].setTitle(
            'Conversion format for dataservice')
    else:
        logger.warn('eea.dataservice conversion vocabulary already exist.')

    # Set public the vocabulary items we use for active convertion
    if convertion_fresh_install:
        for vocabId in CONVERSIONS_USED:
            wftool = getToolByName(site, 'portal_workflow')
            vocabParentOb = getattr(atvm, CONVERSIONS_DICTIONARY_ID)
            vocabItem = getattr(vocabParentOb, vocabId)
            state = wftool.getInfoFor(vocabItem, 'review_state', '(Unknown)')
            if state == 'published':
                continue
            try:
                wftool.doActionFor(vocabItem, 'publish',
                    comment='Auto published by migration script.')
            except Exception:
                logger.debug("eea dataservice setuphandlers migration script "
                             "couldn't auto publish")

def installMimeTypes(context):
    """ Add new mimetypes
    """
    # only run this step if we are in eea.dataservice profile
    if context.readDataFile('eea.dataservice.txt') is None:
        return

    registry = getToolByName(context, 'mimetypes_registry')

    # Database
    register_mimetypes(registry, DB_MIMETYPES)

    # Geographic
    register_mimetypes(registry, GEO_MIMETYPES)
