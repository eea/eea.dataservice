""" The updates package """
from Products.CMFPlone import MigrationTool
from evolve import Evolve

MigrationTool.registerSetupWidget(Evolve)
