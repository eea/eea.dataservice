#
# Script to make all filename and directory names from the file dump lower case
#

import os, sys

path = '/var/local/tmp/dataservicefiles_sharedfiles'

def dataserviceLower(path=''):
    filenames = os.listdir(path)

    for filename in filenames:
        newfilename = filename.lower()
        newpath = os.path.join(path, newfilename)
        origpath = os.path.join(path, filename)
        os.rename(origpath, newpath)
        if os.path.isdir(newpath):
            dataserviceLower(newpath)

dataserviceLower(path)