import json

import requests

from aussieaddonscommon import session
from aussieaddonscommon import utils
from aussieaddonscommon.exceptions import AussieAddonsException

from resources.lib import config
from resources.lib import telstra_auth

import xbmcaddon

try:
    import StorageServer
except Exception:
    utils.log("script.common.plugin.cache not found!")
    import resources.lib.storageserverdummy as StorageServer

cache = StorageServer.StorageServer(utils.get_addon_id(), 1)
sess = session.Session(force_tlsv1=False)
addon = xbmcaddon.Addon()


def clear_ticket():
    """
    Remove stored ticket from cache storage
    """
    cache.delete('SOCCERTICKET')
    utils.dialog_message('Login token removed')


def get_user_ticket():
    """
    send user login info and retrieve ticket for session
    """
    stored_ticket = cache.get('SOCCERTICKET')
    if stored_ticket != '':
        utils.log('Using ticket: {0}******{1}******'.format(
            stored_ticket[:8], stored_ticket[15:-6]))
        return stored_ticket
    else:
        subscription_type = int(addon.getSetting('SUBSCRIPTION_TYPE'))
        if subscription_type == 0:
            auth = telstra_auth.TelstraAuth(
                addon.getSetting('LIVE_USERNAME'),
                addon.getSetting('LIVE_PASSWORD'))
            ticket = auth.get_free_token()
        elif subscription_type == 2:
            auth = telstra_auth.TelstraAuth(
                addon.getSetting('PAID_USERNAME'),
                addon.getSetting('PAID_PASSWORD'))
            ticket = auth.get_paid_token()
        else:
            auth = telstra_auth.TelstraAuth()
            ticket = auth.get_mobile_token()
    cache.set('SOCCERTICKET', ticket)
    return ticket


def get_media_auth_token(pai, bearer, video_id):
    """
    send our user token to get our embed token, including api key
    """
    url = config.MEDIA_AUTH_URL.format(code=video_id, pai=pai)
    sess.headers = {}
    sess.headers.update(
        {'Authorization': 'Bearer {0}'.format(bearer),
         'Accept-Encoding': 'gzip'})
    try:
        req = sess.get(url)
        data = req.text
        json_data = json.loads(data)
        if json_data.get('Fault'):
            raise AussieAddonsException(
                json_data.get('fault').get('faultstring'))
        media_auth_token = json_data.get('token')
    except requests.exceptions.HTTPError as e:
        utils.log('Error getting embed token. '
                  'Response: {0}'.format(e.response.text))
        cache.delete('SOCCERTICKET')
        if e.response.status_code == 401:
            raise AussieAddonsException('Login token has expired, '
                                        'please try again.')
        else:
            raise e
    return media_auth_token
