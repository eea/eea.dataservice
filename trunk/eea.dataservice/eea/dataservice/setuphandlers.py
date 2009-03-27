from Products.ATVocabularyManager.utils.vocabs import createHierarchicalVocabs, createSimpleVocabs
from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL
from Products.CMFCore.utils import getToolByName
from eea.dataservice.vocabulary import COUNTRIES_DICTIONARY_ID, getCountriesDictionary
from eea.dataservice.vocabulary import CATEGORIES_DICTIONARY_ID, CATEGORIES_DICTIONARY
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
        hierarchicalVocab[(COUNTRIES_DICTIONARY_ID, 'Dataservice Countries')] = {}
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

    # Create categories vocabulary
    if not CATEGORIES_DICTIONARY_ID in atvm.contentIds():
        createSimpleVocabs(atvm, CATEGORIES_DICTIONARY)
        atvm[CATEGORIES_DICTIONARY_ID].setTitle('Dataservice categories')
    else:
        logger.warn('eea.dataservice categories vocabulary already exist.')
