import os
import sys
import xbmc
import xbmcgui
import xbmcaddon
from urlparse import parse_qsl

addon = xbmcaddon.Addon()
cwd = xbmc.translatePath(addon.getAddonInfo('path')).decode("utf-8")
BASE_RESOURCE_PATH = os.path.join(cwd, 'resources', 'lib')
sys.path.append(BASE_RESOURCE_PATH)

import play  # noqa: E402
import menus  # noqa: E402
import ooyalahelper  # noqa: E402
import categories  # noqa: E402

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
    if params:
        if params['action'] == 'listcategories':
            if params['category'] == 'Live Matches':
                menus.make_live_list(params)
            elif params['category'] == 'Videos':
                menus.make_video_list(params)
            elif params['category'] == 'Settings':
                addon.openSettings()
        elif params['action'] == 'listvideos':
            play.play_video(params)
        elif params['action'] == 'clearticket':
            ooyalahelper.clear_ticket()
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
