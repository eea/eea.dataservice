""" Vocabularies
"""
from zope.schema.interfaces import IVocabularyFactory
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm

class EconomicSectors(object):
    """ Economic Sectors
    """
    implements(IVocabularyFactory)

    def __call__(self, context=None):
        """ See IVocabularyFactory interface
        """
        items = (
            SimpleTerm('agriculture', 'agriculture', 'Agriculture'),
            SimpleTerm('demography', 'demography', 'Demography'),
            SimpleTerm('energy', 'energy', 'Energy'),
            SimpleTerm('environment', 'environment', 'Environment'),
            SimpleTerm('education', 'education', 'Education'),
            SimpleTerm('forestry', 'forestry', 'Forestry'),
            SimpleTerm('health', 'health', 'Health'),
            SimpleTerm('physical-planning', 'physical-planning',
                       'Physical planning'),
            SimpleTerm('research', 'research', 'Research'),
            SimpleTerm('tourism', 'tourism', 'Tourism'),
            SimpleTerm('transport', 'transport', 'Transport'),
        )
        return SimpleVocabulary(items)

class EnvironmentalDomains(object):
    """ Environmental Domains
    """
    implements(IVocabularyFactory)

    def __call__(self, context=None):
        """ See IVocabularyFactory interface
        """
        items = (
            SimpleTerm('air-pollution', 'air-pollution', 'Air pollution'),
            SimpleTerm('climate-change', 'climate-change', 'Climate change'),
            SimpleTerm('coastal-zone', 'coastal-zone', 'Coastal zone'),
            SimpleTerm('hazardous-substances', 'hazardous-substances',
                       'Hazardous substances'),
            SimpleTerm('marine-environment', 'marine-environment',
                       'Marine environment'),
            SimpleTerm('ozone-depletion', 'ozone-depletion', 'Ozone depletion'),
            SimpleTerm('nature-conservation', 'nature-conservation',
                       'Nature conservation'),
            SimpleTerm('soil-degradation', 'soil-degradation',
                       'Soil degradation'),
            SimpleTerm('transboundary-issues', 'transboundary-issues',
                       'Transboundary issues'),
            SimpleTerm('urban-environment', 'urban-environment',
                       'Urban environment'),
            SimpleTerm('waste-management', 'waste-management',
                       'Waste management'),
            SimpleTerm('water-management', 'water-management',
                       'Water management'),
        )
        return SimpleVocabulary(items)
