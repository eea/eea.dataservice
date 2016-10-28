""" Installer
"""
import os
from os.path import join
from setuptools import setup, find_packages

name = 'eea.dataservice'
path = name.split('.') + ['version.txt']
version = open(join(*path)).read().strip()

setup(name=name,
      version=version,
      description="EEA Data service",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='eea, dataservice, data, service, datasets',
      author=('Alec Ghica (Eaudeweb), Alin Voinea (Eaudeweb), '
              'Antonio De Marinis (EEA), European Environment Agency'),
      author_email='webadmin@eea.europa.eu',
      url='http://www.eea.europa.eu/data-and-maps',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['eea'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Pillow',
          'rarfile',
          'Products.ATVocabularyManager',
          'Products.CMFPlacefulWorkflow',
          'eea.cache',
          'eea.jquery',
          'eea.versions',
          'eea.forms',
          'eea.vocab',
          'eea.workflow',
          'eea.geotags',
          'five.intid',
          'plone.app.async',
          'eea.indicators',
          'collective.quickupload',
          'eventlet',
      ],
      extras_require={
          'test': ['plone.app.testing',]
      },
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
