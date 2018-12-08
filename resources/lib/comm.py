import classes
import config
import json

from aussieaddonscommon import session


def fetch_url(url, headers=None):
    """
    HTTP GET on url, remove byte order mark
    """
    with session.Session() as sess:
        if headers:
            sess.headers = headers
        resp = sess.get(url)
        return resp.text.encode("utf-8")


def list_videos(params):
    data = json.loads(fetch_url(config.VIDEOS_URL))
    listing = []
    for video in data:
        v = classes.Video()
        v.title = video.get('name')
        v.desc = video.get('name')
        v.thumb = video.get('poster_small').get('url')
        v.fanart = video.get('poster').get('url')
        v.video_id = video.get('video_id')
        v.account_id = video.get('account_id')
        listing.append(v)
    return listing


def list_live(params):
    data = json.loads(fetch_url(config.HOME_URL))
    listing = []
    for match in data.get('upcoming_matches'):
        match_data = match.get('match')
        if not match:
            continue
        if match_data.get('status') == 'FullTime':
            continue
        broadcasters = match_data.get('broadcasters')
        if not broadcasters:
            continue
        v = classes.Video()
        v.home = match_data.get('home_team').get('name')
        v.away = match_data.get('away_team').get('name')
        v.start_date = match_data.get('start_date')
        v.status = match_data.get('status')
        if v.status == 'PreMatch' and v.is_near_live():
            v.status == 'Live'
        if v.status == 'Live':
            v.live = True
            v.title = v.get_live_title()
            for broadcast in broadcasters:
                if 'Telstra' in broadcast.get('name'):
                    v.ooyala_id = broadcast.get('stream_name')
                    break
        else:
            v.dummy = True
            v.title = v.get_upcoming_title()
        listing.append(v)
    return listing


def get_stream_url(account_id, video_id):
    policy = config.BC_POLICYS[account_id]
    bc_url = config.BC_URL.format(account_id, video_id)
    data = json.loads(fetch_url(bc_url, {'BCOV-POLICY': policy}))
    for source in data.get('sources'):
        ext_ver = source.get('ext_x_version')
        src = source.get('src')
        if ext_ver == '4' and src:
            if src.startswith('https'):
                return src
