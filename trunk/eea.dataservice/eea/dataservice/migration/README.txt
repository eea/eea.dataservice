Migrate old dataservice
=======================

Migration steps:
    - Site setup -> install "eea.dataservice" product

Under portal_setup:
    - use 'EEA Dataservice' profile
    - Import -> "Types Tool"
                    (Products.CMFCore.exportimport.typeinfo.importTypesTool)
    - Import -> "Install Vocabularies for eea.dataservice"
                    (eea.dataservice.setuphandlers.installVocabularies)

Run:
    - @@migrate_organisations
    - @@migrate_datasets
    - //@@migrate_tables_files
    - //@@migrate_datarelations

Plone customisations:
    - Put under portal_skins/custom/standard_error_message
         the content of eea.dataservice/eea/dataservice/migration/standard_error_message.py
         to make redirects work
    - Site setup -> Kupu visual editor -> toolbar
        (http://eea.europa.eu/kupu_library_tool/zmi_toolbar)
        Make "Subscript/Superscript group" visible to activate
          subscript and superscript in Kupu.

