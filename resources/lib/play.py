import classes
import comm
import json
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

        embed_token = None
        if v.premium:
            auth = json.loads(ooyalahelper.get_user_ticket())
            embed_token = ooyalahelper.get_embed_token(auth.get('pai'),
                                                       auth.get('bearer'),
                                                       v.video_id)
        v.url = comm.get_stream_url(v, embed_token)
        if not v.url:
            raise Exception('Unable to find stream for video')
        play_item = xbmcgui.ListItem(path=v.url,
                                     iconImage=v.thumb,
                                     thumbnailImage=v.thumb)
        if not v.live:
            play_item.setProperty('inputstreamaddon', 'inputstream.adaptive')
            play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
        xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)
    except Exception:
        utils.handle_error('Unable to play video')
