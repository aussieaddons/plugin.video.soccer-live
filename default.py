import os
import sys

from future.moves.urllib.parse import parse_qsl

from aussieaddonscommon import utils

from resources.lib import categories
from resources.lib import menus
from resources.lib import play
from resources.lib import stream_auth

import xbmcaddon

import xbmcgui

addon = xbmcaddon.Addon()
_url = sys.argv[0]
_handle = int(sys.argv[1])
addonname = addon.getAddonInfo('name')
addonPath = xbmcaddon.Addon().getAddonInfo("path")
fanart = os.path.join(addonPath, 'fanart.jpg')


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring
    :param paramstring:
    """
    params = dict(parse_qsl(paramstring))
    utils.log('addon called with params: {0}'.format(str(params)))
    if params:
        if params['action'] == 'listcategories':
            if params['category'] == 'Live Matches':
                menus.make_live_list(params)
            elif params['category'] == 'Match Replays':
                menus.make_comp_list(params)
            elif params['category'] == 'Videos':
                menus.make_video_list(params)
            elif params['category'] == 'Settings':
                addon.openSettings()
        elif params['action'] == 'listcomps':
            if params['type'] == 'competition':
                menus.make_round_list(params)
            else:
                menus.make_replay_list(params)
        elif params['action'] == 'listrounds':
            menus.make_replay_list(params)
        elif params['action'] in ['listvideos', 'listreplays']:
            play.play_video(params)
        elif params['action'] == 'clearticket':
            stream_auth.clear_ticket()
        elif params['action'] == 'open_ia_settings':
            try:
                import drmhelper
                if drmhelper.check_inputstream(drm=False):
                    ia = drmhelper.get_addon()
                    ia.openSettings()
                else:
                    utils.dialog_message(
                        "Can't open inputstream.adaptive settings")
            except Exception:
                utils.dialog_message(
                    "Can't open inputstream.adaptive settings")
    else:
        categories.list_categories()


if __name__ == '__main__':
    if addon.getSetting('firstrun') == 'true':
        xbmcgui.Dialog().ok(addonname, ('Please enter your My Football Live '
                                        'Pass (Telstra ID) username and '
                                        'password to access the content '
                                        'in this service.'))
        addon.openSettings()
        addon.setSetting('firstrun', 'false')
    router(sys.argv[2][1:])
