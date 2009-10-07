from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='eea.dataservice',
      version=version,
      description="EEA Dataservice",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='eea, dataservice, data, service',
      author='European Environment Agency',
      author_email='alec.ghica@eaudeweb.ro',
      url='http://dataservice.eea.europa.eu',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['eea'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
