import classes
import config
import json

from aussieaddonscommon import session, utils


def fetch_url(url, headers=None):
    """
    HTTP GET on url, remove byte order mark
    """
    with session.Session() as sess:
        if headers:
            sess.headers = headers
        resp = sess.get(url)
        return resp.text.encode("utf-8")


def list_comps(params):
    data = json.loads(fetch_url(config.CONFIG_URL))
    listing = []
    for comp in data.get('hub_configuration'):
        c = classes.Category()
        c.title = comp.get('long_name')
        c.thumb = comp['small'].get('url')
        c.type = comp.get('type')
        c.active_season = comp.get('active_season')
        if c.type == 'competition':
            c.id = str(comp.get('competition_id'))
        else:
            c.id = str(comp.get('team_id'))
        listing.append(c)
    return listing


def list_rounds(params):
    comp_id = params.get('id')
    active_season = params.get('active_season')
    data = json.loads(fetch_url(config.MATCHES_URL.format(
        'c{0}/s{1}/summary'.format(comp_id, active_season))))
    listing = []
    current_round = int(
        data.get('round_info').get('active_round').get('number'))
    round_data = data.get('round_info').get('rounds')
    for rnd in range(current_round, 0, -1):
        c = classes.Category()
        c.title = round_data[rnd-1].get('name')
        c.thumb = params.get('thumb')
        c.rnd = str(rnd)
        c.id = comp_id
        c.active_season = active_season
        listing.append(c)
    return listing


def list_matches(params):
    comp_id = params.get('id')
    rnd = params.get('rnd')
    active_season = params.get('active_season')
    if params.get('type') == 'team':
        query = 't{0}/fixture'.format(comp_id)
        data = json.loads(fetch_url(config.MATCHES_URL.format(query)))
        listing = []
        round_data = [entry.get('match') for entry in data]
    else:
        query = 'c{0}/s{1}/r{2}/fixture'.format(comp_id, active_season, rnd)
        data = json.loads(fetch_url(config.MATCHES_URL.format(query)))
        listing = []
        round_data = data.get('rounds')
    for match in round_data:
        v = classes.Video()
        v.ooyala_id = match.get('match_replay_embedcode')
        if not v.ooyala_id:
            continue
        v.title = match.get('title')
        v.desc = match.get('title')
        v.thumb = params.get('thumb')
        listing.append(v)
    return listing


def list_videos(params):
    data = json.loads(fetch_url(config.VIDEOS_URL))
    listing = []
    for video in data:
        if not video.get('poster'):
            continue
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
            v.status = 'Live'
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
    config_data = json.loads(fetch_url(config.CONFIG_URL))
    policy = None
    for acc in config_data['video_settings']:
        if acc.get('account_id') == account_id:
            policy = acc.get('policy_key')
    if not policy:
        raise Exception("Can't retrieve brightcove policy key")
    bc_url = config.BC_URL.format(account_id, video_id)
    data = json.loads(fetch_url(bc_url, {'BCOV-POLICY': policy}))
    src = None
    for source in data.get('sources'):
        ext_ver = source.get('ext_x_version')
        src = source.get('src')
        if ext_ver == '4' and src:
            if src.startswith('https'):
                return src
    if not src:
        utils.log(data.get('sources'))
        raise Exception('Unable to locate video source.')