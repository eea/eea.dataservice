Migrate old Maps & Graphs
=========================
Only for Demo use:
    - run buildout with dataservice-deploymen.cfg or dataservice-devel.cfg
        depending of your demo environmet (deployment or devel)

NOTE: for demo use be advise not to import all figures as the process can take long time.

On server update/install Ghostscript to version 8.64 to ensure that convertions
of different EPS files works fine. PIL is using Ghostscript when converting EPS files.
(http://pages.cs.wisc.edu/~ghost/doc/GPL/gpl864.htm)

Migration steps:
    - Site setup -> install "eea.mapsandgraphs" product
    - Site setup -> install "eea.dataservice" product
    - Site setup -> install "iw.fss" product

Run:
    - http://plone_site/SITE/@@migrate_organisations
    - http://plone_site/SITE/@@migrate_figures
    - http://plone_site/SITE/@@migrate_figurerelations

    Two new folders will be created under /SITE . One containing organisations
      and a second one containing some figures. (for demo purpose just a few
      datasets are imported at this point)

Migrate old dataservice
=======================

Migration steps:
    - Edit file ../buildout/src/eea.dataservice/eea/dataservice/migration/config.py
       and modify the value of DATAFILES_PATH to fit the files dump path
       If using files dump from Whiteshark the DATAFILES_PATH should be:
            DATAFILES_PATH = os.path.join('/var/eeawebtest/dataservicefiles')
    - Restart server

Run:
    - http://plone_site/SITE/@@migrate_datasets
    - http://plone_site/SITE/@@migrate_datarelations

    One new folders /SITE/data will be created.

Plone customisations:
    - Put under ../portal_skins/custom/standard_error_message
         the content of eea.dataservice/eea/dataservice/migration/standard_error_message.py
         to make redirects work
    - Site setup -> Kupu visual editor -> toolbar
        (http://eea.europa.eu/kupu_library_tool/zmi_toolbar)
        Make "Subscript/Superscript group" visible to activate
          subscript and superscript in Kupu.
