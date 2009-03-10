class Dataset(object):
    """ Encapsulate report
    """
    def __init__(self):
        """ """
        pass

class dataservice_handler(ContentHandler):
    """ """

    def __init__(self):
        """ constructor """
        self.datasets = []

    def get_datasets(self):
        return self.datasets

    def get_mapsandgraphs(self):
        pass
    
    def startElement(self, name, attrs):
        pass

    def endElement(self, name):
        pass

    def characters(self, content):
        pass

class dataservice_parser:
    """ """

    def __init__(self):
        """ """
        pass

    def parseContent(self, xml_string):
        """ """
        chandler = dataservice_handler()
        parser = make_parser()
        parser.setContentHandler(chandler)
        parser.setFeature(chandler.feature_external_ges, 0)
        inpsrc = InputSource()
        inpsrc.setByteStream(StringIO(xml_string))
        parser.parse(inpsrc)
        return chandler

    def parseHeader(self, file):
        parser = make_parser()
        chandler = dataservice_handler()
        parser.setContentHandler(chandler)
        try:    parser.setFeature(chandler.feature_external_ges, 0)
        except: pass
        inputsrc = InputSource()

        if type(file) is StringType:
            inputsrc.setByteStream(StringIO(file))
        else:
            filecontent = file.read()
            inputsrc.setByteStream(StringIO(filecontent))
        parser.parse(inputsrc)
        return chandler

def extract_data(file_id=''):
    """ Return data from old dataservice exported XMLs
    """
    f = open(file_id);
    s = f.read()
    parser = dataservice_parser()
    data = parser.parseHeader(s)
    return data.get_datasets()

if __name__ == '__main__':
    print len(extract_data())