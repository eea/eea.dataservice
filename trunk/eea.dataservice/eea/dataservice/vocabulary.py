from datetime import datetime
from zope.interface import implements
from zope.app.schema.vocabulary import IVocabularyFactory
from eea.dataservice.config import *


class DatasetYearsVocabularyFactory(object):
    """ Dataset years vocabulary
    """
    implements(IVocabularyFactory,)
    
    def __call__(self):
        now = datetime.now()
        end_year = now.year + 3
        terms = []
        terms.extend((str(key), str(key))
                     for key in reversed(range(STARTING_YEAR, end_year)))
        return terms

DatasetYearsVocabulary = DatasetYearsVocabularyFactory()