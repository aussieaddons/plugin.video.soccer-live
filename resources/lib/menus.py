import sys

from aussieaddonscommon import utils

from resources.lib import comm

import xbmcaddon

import xbmcgui

import xbmcplugin

_url = sys.argv[0]
_handle = int(sys.argv[1])
addon_path = xbmcaddon.Addon().getAddonInfo("path")


def make_replay_list(params):
    try:
        listing = []
        matches = comm.list_matches(params)

        for m in matches:
            li = xbmcgui.ListItem(label=m.title)
            li.setArt({'icon': m.thumb, 'thumb': m.thumb})
            url = '{0}?action=listreplays{1}'.format(_url, m.make_kodi_url())
            is_folder = False
            li.setProperty('IsPlayable', 'true')
            li.setInfo('video', {'plot': m.title, 'plotoutline': m.title})
            listing.append((url, li, is_folder))

        xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
        xbmcplugin.endOfDirectory(_handle)
    except Exception:
        utils.handle_error('Unable to display match replays')


def make_round_list(params):
    try:
        listing = []
        rounds = comm.list_rounds(params)

        for r in rounds:
            li = xbmcgui.ListItem(label=r.title)
            li.setArt({'icon': r.thumb, 'thumb': r.thumb})
            url = '{0}?action=listrounds{1}'.format(_url, r.make_kodi_url())
            is_folder = True
            li.setProperty('IsPlayable', 'false')
            li.setInfo('video', {'plot': r.title, 'plotoutline': r.title})
            listing.append((url, li, is_folder))

        xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
        xbmcplugin.endOfDirectory(_handle)
    except Exception:
        utils.handle_error('Unable to display rounds')


def make_comp_list(params):
    try:
        listing = []
        comps = comm.list_comps(params)

        for c in comps:
            li = xbmcgui.ListItem(label=c.title)
            li.setArt({'icon': c.thumb, 'thumb': c.thumb})
            url = '{0}?action=listcomps{1}'.format(_url, c.make_kodi_url())
            is_folder = True
            li.setProperty('IsPlayable', 'false')
            li.setInfo('video', {'plot': c.title, 'plotoutline': c.title})
            listing.append((url, li, is_folder))

        xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
        xbmcplugin.endOfDirectory(_handle)
    except Exception:
        utils.handle_error('Unable to display comps')


def make_video_list(params):
    """
    Build video listing for Kodi
    """
    try:
        listing = []
        videos = comm.list_videos(params)

        for v in videos:
            li = xbmcgui.ListItem(label=v.title)
            li.setArt({'icon': v.thumb, 'thumb': v.thumb})
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
            li = xbmcgui.ListItem(label=v.title)
            li.setArt({'icon': v.thumb, 'thumb': v.thumb})
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
