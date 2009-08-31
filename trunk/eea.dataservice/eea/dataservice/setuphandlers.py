from Products.ATVocabularyManager.utils.vocabs import createHierarchicalVocabs, createSimpleVocabs
from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL
from Products.CMFCore.utils import getToolByName
from eea.dataservice.vocabulary import COUNTRIES_DICTIONARY_ID, getCountriesDictionary
from eea.dataservice.vocabulary import CATEGORIES_DICTIONARY_ID, CATEGORIES_DICTIONARY
from eea.dataservice.vocabulary import QUALITY_DICTIONARY_ID, QUALITY_DICTIONARY
from eea.dataservice.vocabulary import REFERENCE_DICTIONARY_ID, REFERENCE_DICTIONARY
from eea.dataservice.vocabulary import QLD_DICTIONARY_ID, QLD_DICTIONARY
from eea.dataservice.vocabulary import QLMG_DICTIONARY_ID, QLMG_DICTIONARY
import logging
logger = logging.getLogger('eea.dataservice: setuphandlers')

def installVocabularies(context):
    """creates/imports the atvm vocabs."""

    site = context.getSite()
    try:
        atvm = getToolByName(site, ATVOCABULARYTOOL)
    except AttributeError:
        qinstaller = getToolByName(site, 'portal_quickinstaller')
        qinstaller.installProduct('ATVocabularyManager')
        atvm = getToolByName(site, ATVOCABULARYTOOL)

    # Creat countries vocabulary
    if not COUNTRIES_DICTIONARY_ID in atvm.contentIds():
        hierarchicalVocab = {}
        hierarchicalVocab[(COUNTRIES_DICTIONARY_ID, 'European Countries')] = {}
        createHierarchicalVocabs(atvm, hierarchicalVocab)

        countries = getCountriesDictionary()
        for term in countries.keys():
            vocab = atvm[COUNTRIES_DICTIONARY_ID]
            vocab.invokeFactory('TreeVocabularyTerm', term[0], title=term[1])
            for subterm in countries[term].keys():
                subvocab = vocab[term[0]]
                subvocab.invokeFactory('TreeVocabularyTerm', subterm[0], title=subterm[1])
                subvocab.reindexObject()
            vocab.reindexObject()
    else:
        logger.warn('eea.dataservice countries vocabulary already exist.')

    # Create reference vocabulary
    if not REFERENCE_DICTIONARY_ID in atvm.contentIds():
        createSimpleVocabs(atvm, REFERENCE_DICTIONARY)
        atvm[REFERENCE_DICTIONARY_ID].setTitle('Coordinate reference system')
    else:
        logger.warn('eea.dataservice reference vocabulary already exist.')

    # Create quality vocabulary
    if not QUALITY_DICTIONARY_ID in atvm.contentIds():
        createSimpleVocabs(atvm, QUALITY_DICTIONARY)
        atvm[QUALITY_DICTIONARY_ID].setTitle('Geographic information quality')
    else:
        logger.warn('eea.dataservice quality vocabulary already exist.')

    # Create quick link vocabulary for datasets
    if not QLD_DICTIONARY_ID in atvm.contentIds():
        createSimpleVocabs(atvm, QLD_DICTIONARY)
        atvm[QLD_DICTIONARY_ID].setTitle('Datasets quick links')
    else:
        logger.warn('eea.dataservice quick link vocabulary for datasets already exist.')

    # Create quick link vocabulary for maps and graphs
    if not QLMG_DICTIONARY_ID in atvm.contentIds():
        createSimpleVocabs(atvm, QLMG_DICTIONARY)
        atvm[QLMG_DICTIONARY_ID].setTitle('Maps & graphs quick links')
    else:
        logger.warn('eea.dataservice quick link vocabulary for maps and graphs already exist.')

    # Create categories vocabulary
    if not CATEGORIES_DICTIONARY_ID in atvm.contentIds():
        createSimpleVocabs(atvm, CATEGORIES_DICTIONARY)
        atvm[CATEGORIES_DICTIONARY_ID].setTitle('Dataservice categories')
    else:
        logger.warn('eea.dataservice categories vocabulary already exist.')
