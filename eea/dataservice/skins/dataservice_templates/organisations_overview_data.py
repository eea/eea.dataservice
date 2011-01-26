## Script (Python) "organisations overview"
##title=Organisations overview
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=

from Products.CMFCore.utils import getToolByName

request = context.REQUEST
response = request.RESPONSE

cat = getToolByName(context, 'portal_catalog', None)

query = {
'show_inactive':True,
'language':'ALL',
'portal_type': 'Organisation',}

brains = cat(**query)

data = {}
full_data = {}
res = []

for k in brains:
 org_url = k.getUrl
 data[org_url] = 0
 full_data[org_url] = k

 query = {'portal_type':['EEAFigure','Data'], 'getDataOwner': org_url}
 owner_brains = cat(**query)
 data[org_url] = data[org_url] + len(owner_brains)

 query = {'portal_type':['EEAFigure','Data'], 'getProcessor': org_url}
 proc_brains = cat(**query)
 data[org_url] = data[org_url] + len(proc_brains)

for k in data.keys():
 if data[k] == 0:
  res.append(full_data[k])

return res
