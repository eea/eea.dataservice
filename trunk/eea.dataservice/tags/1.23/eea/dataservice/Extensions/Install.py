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

    # DCWorkflowDump doesn't yet support the 'manager_bypass'
    WF_IDs = ['eea_data_workflow', 'eea_imagefs_workflow']
    wf_tool = getToolByName(portal, 'portal_workflow')
    for wf_id in WF_IDs:
        if wf_id in wf_tool.objectIds():
            wfobj = wf_tool.getWorkflowById(wf_id)
            wfobj.manager_bypass = 1

    # enable portal_factory for given types
    factory_tool = getToolByName(portal, 'portal_factory')
    factory_types=[
        "Data",
        "DataFile",
        "DataTable",
        "EEAFigure",
        "EEAFigureFile",
        "Organisation",
        "ImageFS",
        ] + factory_tool.getFactoryTypes().keys()
    factory_tool.manage_setPortalFactoryTypes(listOfTypeIds=factory_types)

    return "Ran all import steps."