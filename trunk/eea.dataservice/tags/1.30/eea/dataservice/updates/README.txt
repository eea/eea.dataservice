eea.dataservice updates package
===============================

1. +++ evolve.py +++
    * #3595 - Fix low resolution images for EEA Figure Files
    * in portal_vocabularies/conversions update available conversions
        * Unpublish or delete low resolution ones
          [PNG-75, GIF-100, TIFF-100, PNG-100]
        *Add and publish new conversion items [PNG-300, GIF-300, TIFF-300]
    * in ZMI >  portal_migrations > Setup Tab
      run "Fix low resolution images for EEA Figure Files" step

2. +++ soer_bulk_import.py +++
    * see more details under #3987
    * change IMPORT_PATH and FILES_PATH accordingly under soer_bulk_import.py
    * run @@migrate_soer_figures in order to start import of SOER figures
