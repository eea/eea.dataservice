Migrate old dataservice
=======================

Only for Demo use:
    - run buildout with dataservice-deploymen.cfg or dataservice-devel.cfg
        depending of your demo environmet (deployment or devel)

Migration steps:
    - Site setup -> install "eea.dataservice" product
    - Site setup -> install "iw.fss" product
    - Edit file ../buildout/src/eea.dataservice/eea/dataservice/migration/config.py
       and modify the value of DATAFILES_PATH to fit the files dump path
    - Restart server

Run:
    - http://plone_site/@@migrate_organisations
    - http://plone_site/@@migrate_datasets

    Two new folders will be created under /SITE . One containing organisations
      and a second one containing some datasets. (for demo purpose just a few
      datasets are imported at this point)

Plone customisations:
    - Put under ../portal_skins/custom/standard_error_message
         the content of eea.dataservice/eea/dataservice/migration/standard_error_message.py
         to make redirects work
    - Site setup -> Kupu visual editor -> toolbar
        (http://eea.europa.eu/kupu_library_tool/zmi_toolbar)
        Make "Subscript/Superscript group" visible to activate
          subscript and superscript in Kupu.

