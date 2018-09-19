import urllib
import json
import base64
import config
import re
import requests
import xbmcaddon
import telstra_auth

from aussieaddonscommon.exceptions import AussieAddonsException
from aussieaddonscommon import session
from aussieaddonscommon import utils

try:
    import StorageServer
except:
    utils.log("script.common.plugin.cache not found!")
    import storageserverdummy as StorageServer
cache = StorageServer.StorageServer(config.ADDON_ID, 1)
sess = session.Session(force_tlsv1=False)
addon = xbmcaddon.Addon()
username = addon.getSetting('LIVE_USERNAME')
password = addon.getSetting('LIVE_PASSWORD')


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
        utils.log('Using ticket: {0}******'.format(stored_ticket[:-6]))
        return stored_ticket
    else:
        ticket = telstra_auth.get_free_token(username, password)
    cache.set('SOCCERTICKET', ticket)
    return ticket


def get_embed_token(user_token, video_id):
    """
    send our user token to get our embed token, including api key
    """
    url = config.EMBED_TOKEN_URL.format(video_id)
    sess.headers.update({'X-YinzCam-Ticket': user_token,
                         'Accept': 'application/json'})
    try:
        req = sess.get(url)
        data = req.text
        json_data = json.loads(data)
        if json_data.get('ErrorCode') is not None:
            raise AussieAddonsException()
        video_token = json_data.get('VideoToken')
    except requests.exceptions.HTTPError as e:
        utils.log('Error getting embed token. '
                  'Response: {0}'.format(e.response.text))
        cache.delete('NETBALLTICKET')
        if e.response.status_code == 401:
            raise AussieAddonsException('Login token has expired, '
                                        'please try again.')
        else:
            raise e
    return urllib.quote(video_token)


def get_secure_token(secure_url, videoId):
    """
    send our embed token back with a few other url encoded parameters
    """
    res = sess.get(secure_url)
    data = res.text
    try:
        parsed_json = json.loads(data)
        token = (parsed_json['authorization_data'][videoId]
                 ['streams'][0]['url']['data'])
    except KeyError:
        utils.log('Video ID: {0}'.format(videoId))
        utils.log('Parsed json data: {0}'.format(parsed_json))
        try:
            auth_msg = parsed_json['authorization_data'][videoId]['message']
            if auth_msg == 'unauthorized location':
                country = parsed_json['user_info']['country']
                raise AussieAddonsException('Unauthorised location for '
                                            'streaming. '
                                            'Detected location is: {0}. '
                                            'Please check VPN/smart DNS '
                                            'settings '
                                            ' and try again'.format(country))
        except Exception as e:
            raise e
    return base64.b64decode(token)


def get_m3u8_streams(secure_token_url):
    """
    fetch our m3u8 file which contains streams of various qualities
    """
    res = sess.get(secure_token_url)
    data = res.text.splitlines()
    return data


def parse_m3u8_streams(data, live, secure_token_url):
    """
    Parse the retrieved m3u8 stream list into a list of dictionaries
    then return the url for the highest quality stream. Different
    handling is required of live m3u8 files as they seem to only contain
    the destination filename and not the domain/path.
    """
    if live:
        qual = int(addon.getSetting('LIVEQUALITY'))
        if qual == config.MAX_LIVEQUAL:
            qual = -1
        # fix for values too high from previous API config
        if qual > config.MAX_LIVEQUAL:
            addon.setSetting('LIVEQUALITY', str(config.MAX_LIVEQUAL))
            qual = -1
    else:
        qual = int(addon.getSetting('REPLAYQUALITY'))
        if qual == config.MAX_REPLAYQUAL:
            qual = -1
        # fix for values too high from previous API config
        if qual > config.MAX_REPLAYQUAL:
            addon.setSetting('REPLAYQUALITY', str(config.MAX_REPLAYQUAL))
            qual = -1

    m3u_list = []
    base_url = secure_token_url[:secure_token_url.rfind('/') + 1]
    base_domain = secure_token_url[:secure_token_url.find('/', 8) + 1]
    m3u8_lines = iter(data)
    for line in m3u8_lines:
            stream_inf = '#EXT-X-STREAM-INF:'
            if line.startswith(stream_inf):
                line = line[len(stream_inf):]
            else:
                continue

            csv_list = re.split(',(?=(?:(?:[^"]*"){2})*[^"]*$)', line)
            linelist = [i.split('=') for i in csv_list]

            uri = next(m3u8_lines)

            if uri.startswith('/'):
                linelist.append(['URL', base_domain + uri])
            elif uri.find('://') == -1:
                linelist.append(['URL', base_url + uri])
            else:
                linelist.append(['URL', uri])
            m3u_list.append(dict((i[0], i[1]) for i in linelist))
    sorted_m3u_list = sorted(m3u_list, key=lambda k: int(k['BANDWIDTH']))
    try:
        stream = sorted_m3u_list[qual]['URL']
    except IndexError as e:
        utils.log('Quality setting: {0}'.format(qual))
        utils.log('Sorted m3u8 list: {0}'.format(sorted_m3u_list))
        raise e
    return stream


def get_m3u8_playlist(video_id):
    """ Main function to call other functions that will return us our m3u8 HLS
        playlist as a string, which we can then write to a file for Kodi
        to use"""
    #login_token = get_user_ticket()
    #embed_token = get_embed_token(login_token, video_id)
    get_user_ticket()
    authorize_url = config.OOYALA_AUTH_URL.format(config.OOYALA_PCODE,
                                                  video_id)
    secure_token_url = get_secure_token(authorize_url, video_id)

    if 'chunklist.m3u8' in secure_token_url:
        return secure_token_url

    m3u8_data = get_m3u8_streams(secure_token_url)
    m3u8_playlist_url = parse_m3u8_streams(m3u8_data,
                                           live=True,
                                           secure_token_url=secure_token_url)
    return m3u8_playlist_url
