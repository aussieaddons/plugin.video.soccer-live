import xbmcgui
import xbmcplugin
import xbmcaddon
import comm
import sys
from aussieaddonscommon import utils

_url = sys.argv[0]
_handle = int(sys.argv[1])
addon_path = xbmcaddon.Addon().getAddonInfo("path")


def make_video_list(params):
    """
    Build video listing for Kodi
    """
    try:
        listing = []
        videos = comm.list_videos(params)

        for v in videos:
            li = xbmcgui.ListItem(label=v.title,
                                  iconImage=v.thumb,
                                  thumbnailImage=v.thumb)
            url = '{0}?action=listvideos{1}'.format(_url, v.make_kodi_url())
            is_folder = False
            li.setProperty('IsPlayable', 'true')
            li.setInfo('video', {'plot': v.desc, 'plotoutline': v.desc})
            listing.append((url, li, is_folder))

        xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
        xbmcplugin.endOfDirectory(_handle)
    except Exception:
        utils.handle_error('Unable to display matches')


def make_live_list(params):
    """
    Build live match listing for Kodi
    """
    try:
        listing = []
        videos = comm.list_live(params)

        for v in videos:
            li = xbmcgui.ListItem(label=v.title,
                                  iconImage=v.thumb,
                                  thumbnailImage=v.thumb)
            url = '{0}?action=listvideos{1}'.format(_url, v.make_kodi_url())
            is_folder = False
            if not v.dummy:
                li.setProperty('IsPlayable', 'true')
            li.setInfo('video', {'plot': v.desc, 'plotoutline': v.desc})
            listing.append((url, li, is_folder))

        xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
        xbmcplugin.endOfDirectory(_handle, cacheToDisc=False)
    except Exception:
        utils.handle_error('Unable to display matches')
