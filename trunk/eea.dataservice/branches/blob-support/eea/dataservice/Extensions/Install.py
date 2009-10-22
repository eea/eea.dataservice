from Products.CMFCore.utils import getToolByName

def install(portal):
    setup_tool = getToolByName(portal, 'portal_setup')

    # Remove deprecated eea.mapsandgraphs import steps
    ir = setup_tool.getImportStepRegistry()
    try:
        del ir._registered['eea.mapsandgraphs-install-vocabularies']
    except KeyError:
        pass

    # Dataservice import steps
    setup_tool.setImportContext('profile-eea.dataservice:default')
    setup_tool.runAllImportSteps()

    # Uninstall PloneFlashUpload if installed
    product_name = 'PloneFlashUpload'
    qi = getToolByName(portal, 'portal_quickinstaller')
    if qi.isProductInstalled(product_name):
        qi.uninstallProducts([product_name])

    return "Ran all import steps."
