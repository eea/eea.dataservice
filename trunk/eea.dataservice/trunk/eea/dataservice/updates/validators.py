""" Validators
"""
from httplib import HTTP
from urlparse import urlparse
from Products.Five.browser import BrowserView

class LinkChecker(BrowserView):
    """ Generates an report about URLs status based of different properties
        found in indicators dump """

    # From Python CVS urllib2.py
    # Mapping status codes to official W3C names
    http_responses = {
        100: 'Continue',
        101: 'Switching Protocols',
        110: 'Connection timed out',

        200: 'OK',
        201: 'Created',
        202: 'Accepted',
        203: 'Non-Authoritative Information',
        204: 'No Content',
        205: 'Reset Content',
        206: 'Partial Content',

        300: 'Multiple Choices',
        301: 'Moved Permanently',
        302: 'Found',
        303: 'See Other',
        304: 'Not Modified',
        305: 'Use Proxy',
        306: '(Unused)',
        307: 'Temporary Redirect',

        400: 'Bad Request',
        401: 'Unauthorized',
        402: 'Payment Required',
        403: 'Forbidden',
        404: 'Not Found',
        405: 'Method Not Allowed',
        406: 'Not Acceptable',
        407: 'Proxy Authentication Required',
        408: 'Request Timeout',
        409: 'Conflict',
        410: 'Gone',
        411: 'Length Required',
        412: 'Precondition Failed',
        413: 'Request Entity Too Large',
        414: 'Request-URI Too Long',
        415: 'Unsupported Media Type',
        416: 'Requested Range Not Satisfiable',
        417: 'Expectation Failed',

        500: 'Internal Server Error',
        501: 'Not Implemented',
        502: 'Bad Gateway',
        503: 'Service Unavailable',
        504: 'Gateway Timeout',
        505: 'HTTP Version Not Supported',
    }

    def getStatusMsg(self, status_code):
        """ Status message
        """
        return self.http_responses.get(status_code, 'Unknown')

    def getStatusCode(self, url):
        """ Status code
        """
        try:
            p = urlparse(url)
            h = HTTP(p[1])
            h.putrequest('HEAD', p[2])
            h.endheaders()
            return h.getreply()[0]
        except Exception:
            return 110

    def __call__(self, urls=None):
        if urls is None:
            urls = []
        report = {}

        for url in urls:
            status_code = self.getStatusCode(url)
            status_msg = self.getStatusMsg(status_code)
            report[url] = (status_code, status_msg)
        return report
