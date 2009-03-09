from Products.CMFCore.utils import getToolByName

def install(portal):
    #setup_tool = getToolByName(portal, 'portal_setup')
    #setup_tool.setImportContext('profile-eea.dataservice:default')
    #setup_tool.runAllImportSteps()
    return "Ran all import steps."
