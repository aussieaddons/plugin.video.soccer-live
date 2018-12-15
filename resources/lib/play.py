import classes
import comm
import ooyalahelper
import sys
import xbmcaddon
import xbmcgui
import xbmcplugin
from aussieaddonscommon import utils

addon = xbmcaddon.Addon()
_handle = int(sys.argv[1])


def play_video(params):
    """
    Play a video by the provided path.
    :param path: str
    """

    try:
        v = classes.Video()
        v.parse_params(params)
        if v.dummy == 'True':
            xbmcgui.Dialog().ok(
                    'Dummy item',
                    'This item is not playable, it is used only to display '
                    'the upcoming schedule. Please check back once the match '
                    'has started. Playable matches will have "LIVE NOW" in '
                    'green next to the title.')
            return
        if v.ooyala_id:
            v.url = ooyalahelper.get_m3u8_playlist(v.ooyala_id)
        else:
            v.url = comm.get_stream_url(v.account_id, v.video_id)
        play_item = xbmcgui.ListItem(path=v.url,
                                     iconImage=v.thumb,
                                     thumbnailImage=v.thumb)
        xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)
    except Exception:
        utils.handle_error('Unable to play video')
