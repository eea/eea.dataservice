from App.Common import rfc1123_date
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.ResourceRegistries.tools.packer import JavascriptPacker

class Javascript(object):
    """ Handle criteria
    """
    def __init__(self, context, request, resources=()):
        self.context = context
        self.request = request
        self._resources = resources
        self.duration = 3600*24*365

        self.jstool = getToolByName(context, 'portal_javascripts')
        self.debug = self.jstool.getDebugMode()

    @property
    def resources(self):
        """ Return resources
        """
        return self._resources

    def get_resource(self, resource):
        """ Get resource content
        """
        obj = self.context.restrictedTraverse(resource, None)
        if not obj:
            return '/* ERROR */'
        try:
            content = obj.GET()
        except AttributeError, err:
            return str(obj)
        except Exception, err:
            return '/* ERROR: %s */' % err
        else:
            return content

    def get_content(self, **kwargs):
        """ Get content
        """
        output = []
        for resource in self.resources:
            content = self.get_resource(resource)
            header = '\n/* - %s - */\n' % resource
            if not self.debug:
                content = JavascriptPacker('safe').pack(content)
            output.append(header + content)
        return '\n'.join(output)

class ViewJavascript(Javascript):
    """ Javascript libs used in view mode
    """
    @property
    def js_libs(self):
        return [
            '++resource++fancybox/jquery.easing.1.3.js',
            '++resource++fancybox/jquery.fancybox-1.2.1.js',
            '++resource++jqzoom/jqzoom.js',
            '++resource++eea.dataservice.view.js',
        ]

    @property
    def resources(self):
        """ Return view resources
        """
        return self.js_libs

    def __call__(self, *args, **kwargs):
        """ view.js
        """
        self.request.RESPONSE.setHeader('content-type', 'text/javascript')
        expires = rfc1123_date((DateTime() + 365).timeTime())
        self.request.RESPONSE.setHeader('Expires', expires)
        self.request.RESPONSE.setHeader('Cache-Control', 'max-age=%d' % self.duration)
        return self.get_content()
