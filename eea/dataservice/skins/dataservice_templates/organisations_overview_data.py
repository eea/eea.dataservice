## Script (Python) "organisations overview"
##title=Organisations overview
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=info

from Products.CMFCore.utils import getToolByName

request = context.REQUEST
response = request.RESPONSE

cat = getToolByName(context, 'portal_catalog', None)
query = {
'show_inactive':True,
'language':'ALL',
'portal_type': 'Organisation',}
brains = cat(**query)

if info == 'references':
 res = []
 data = {}
 full_data = {}

 for k in brains:
  org_url = k.getUrl
  data[org_url] = 0
  full_data[org_url] = k

  query = {'portal_type':['EEAFigure','Data', 'ExternalDataSpec'],
           'getDataOwner': org_url,
           'show_inactive':True}
  owner_brains = cat(**query)
  data[org_url] = data[org_url] + len(owner_brains)

  query = {'portal_type':['EEAFigure','Data'],
           'getProcessor': org_url,
           'show_inactive':True}
  proc_brains = cat(**query)
  data[org_url] = data[org_url] + len(proc_brains)

  query = {'portal_type':['Specification'],
           'getOwnership': org_url,
           'show_inactive':True}
  spec_brains = cat(**query)
  data[org_url] = data[org_url] + len(spec_brains)

 for k in data.keys():
  if data[k] == 0:
   res.append(full_data[k])
elif info == 'duplicates':
 urls = []
 res = {}
 for k in brains:
  org_url = 'URL: %s' % k.getUrl
  org_title = 'Title: %s' % k.Title.strip()
  urls.append(org_url)
  if org_url.endswith('/'):
   org_url = org_url[:len(org_url)-1]

  if res.has_key(org_url):
   res[org_url].append(k)
  else:
   res[org_url] = [k]

  if res.has_key(org_title):
   res[org_title].append(k)
  else:
   res[org_title] = [k]
else:
 res = None

return res
