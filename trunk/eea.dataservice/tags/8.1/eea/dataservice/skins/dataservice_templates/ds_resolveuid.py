## Script (Python) "resolveuid"
##title=Retrieve an object using its UID
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
# (reference_url is supposed to do the same thing, but is broken)
from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.standard import html_quote
from AccessControl import Unauthorized

request = context.REQUEST
response = request.RESPONSE

try:
    uuid = traverse_subpath.pop(0)
except:
    raise Unauthorized, context

reference_tool = getToolByName(context, 'reference_catalog')
obj = reference_tool.lookupObject(uuid)
if not obj:
    hook = getattr(context, 'kupu_resolveuid_hook', None)
    if hook:
        obj = hook(uuid)
    if not obj:
        # Redirects for version UID
        query = {'getVersionId': uuid,
                 'show_inactive': True,
                 'sort_on': 'effective'}
        resView = context.restrictedTraverse('@@getDataForRedirect')
        res = resView(query)
        if len(res) > 0:
            redirect_to = context.absolute_url() + '/' + res[len(res)-1].getId
            return response.redirect(redirect_to, lock=1)

        # Redirects for short IDs
        if context.getId() == 'figures':
            ptype = 'EEAFigure'
        elif context.getId() == 'data':
            ptype = 'Data'
        else:
            ptype = None

        if ptype:
            query = {'portal_type': ptype,
                     'show_inactive': True,
                     'getShortId': request.get('id', None)}
            resView = context.restrictedTraverse('@@getDataForRedirect')
            res = resView(query)
            if len(res) > 0:
                redirect_to = context.absolute_url() + '/' + res[0].getId
                return context.REQUEST.RESPONSE.redirect(redirect_to, lock=1)

        # Redirects for Not Found
        return response.notFoundError('''The link you followed appears to be broken''')

if traverse_subpath:
    traverse_subpath.insert(0, obj.absolute_url())
    target = '/'.join(traverse_subpath)
else:
    target = obj.absolute_url()

if request.QUERY_STRING:
    target += '?' + request.QUERY_STRING
return response.redirect(target, status=301)
