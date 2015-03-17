""" Custom mime-types
"""
import sys
import csv
from pprint import pprint

if __name__ == "__main__":
    csvfile = sys.argv[1]
    MIMETYPES = ()
    reader = csv.reader(open(csvfile, 'r'), delimiter=',', quotechar='"')
    for row in reader:
        mimetype = {
            'mimetype': row[0],
            'extensions': [x.strip().lower() for x in row[1].split(',')],
            'title': row[2],
            'icon': row[3],
        }
        MIMETYPES += (mimetype,)
    pprint(MIMETYPES)
