""" Test utilities
"""
import os
from StringIO import StringIO

def loadblobfile(context, rel_filename, ctype='application/pdf'):
    """ load a file
    """
    storage_path = os.path.join(os.path.dirname(__file__))
    file_path = os.path.join(storage_path, rel_filename)
    file_ob = open(file_path, 'rb')
    file_data = file_ob.read()
    #size = len(file_data)
    filename = file_path.split('/')[-1]
    filename = str(filename)
    fp = StringIO(file_data)
    fp.filename = filename
    context.setFile(fp)

    return 'File uploaded.'
