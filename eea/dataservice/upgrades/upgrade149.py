"""  Upgrade steps to version 14.8
"""

import logging
import requests
import transaction
import urlparse
import xmltodict
from zope.component.hooks import getSite
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger(__name__)


def migrate_ftp_datafilelinks(context):
    """ Share DataFileLinks with ftp link on CMShare
    """
    ctool = getToolByName(context, 'portal_catalog')
    ptool = getToolByName(context, 'portal_properties')
    cmshare_user = ptool.site_properties.getProperty(
        'cmshare_admin_username', '')
    cmshare_pw = ptool.site_properties.getProperty(
        'cmshare_admin_password', '')

    if cmshare_user == '' or cmshare_pw == '':
        logger.error("CMShare user and password not set in site_properties")
        return

    query = {
        'portal_type': 'DataFileLink',
    }
    brains = ctool.unrestrictedSearchResults(**query)

    logger.info('Sharing DataFileLinks on CMShare')
    count = 0

    get_share_url = 'https://cmshare.eea.europa.eu/ocs/v2.php/apps/' + \
                    'files_sharing/api/v1/shares?path=%s'
    create_share_url = 'https://cmshare.eea.europa.eu/ocs/v2.php/apps/' + \
                        'files_sharing/api/v1/shares?path=%s&shareType=3' + \
                        '&publicUpload=false&permissions=1'
    for brain in brains:
        obj = brain.getObject()
        if 'ftp.eea.europa.eu' in obj.remoteUrl:
            changed = False
            url = None
            path = urlparse.urlparse(obj.remoteUrl).path
            path = path.replace('/www/', '/eea-data-service/').encode('utf-8')

            resp = requests.get(
                get_share_url % path, headers={"OCS-APIRequest": "true"},
                auth=('eeaadmin', 'DJ1O1XbOIU')
            )
            xml = xmltodict.parse(resp.content)

            # first check if share exists, if it doesn't, create share
            if xml['ocs'].get('data', None):
                data = xml['ocs']['data']

                # check if it has more share links, pick the one that is public
                if isinstance(data['element'], list):
                    for elem in data['element']:
                        if elem['shareType'] == '3':
                            url = elem['url']
                            break
                else:
                    url = data['element']['url']
                changed = True
            else:
                # create share link
                res = requests.post(
                    create_share_url % path, headers={"OCS-APIRequest": "true"},
                    auth=('eeaadmin', 'DJ1O1XbOIU')
                )

                if res.status_code == 200:
                    xml = xmltodict.parse(res.content)
                    data = xml['ocs']['data']
                    url = data['url']
                    changed = True
                else:
                    logger.error("Failed to create sharable link for %s" \
                                % brain.getURL())

            if changed and url is not None:
                obj.remoteUrl = url + '/download'
                obj._p_changed = True
                obj.reindexObject()
                count += 1

                logger.info("Succesfully created/retrieved share url and " \
                "modified remoteUrl for: %s" % brain.getURL())
                logger.info("Share url is: %s" % obj.remoteUrl)
            else:
                logger.error("Failed to create/retrieve share for %s" \
                            % brain.getURL())

            if count % 100 == 0:
                logger.info('INFO: Transaction committed to zodb %s', count)
                transaction.commit()

    logger.info('Sharing DataFileLinks on CMShare... DONE')
    return 'Done sharing %s DataFileLinks items' % count