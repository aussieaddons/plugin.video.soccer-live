import datetime
import time
import urlparse
import unicodedata
import urllib


class Video():
    def __init__(self):
        self.video_id = None
        self.thumb = None
        self.title = None
        self.live = None
        self.time = None
        self.desc = None
        self.dummy = None
        self.account_id = None
        self.url = None
        self.home = None
        self.away = None
        self.ooyala_id = None
        self.start_date = None

    def make_kodi_url(self):
        d = self.__dict__
        for key, value in d.iteritems():
            if isinstance(value, unicode):
                d[key] = unicodedata.normalize('NFKD', value).encode('ascii',
                                                                     'ignore')
        url = ''
        if d['thumb']:
            d['thumb'] = urllib.quote_plus(d['thumb'])
        for item in d.keys():
            url += '&{0}={1}'.format(item, d[item])
        return url

    def parse_kodi_url(self, url):
        params = urlparse.parse_qsl(url)
        for item in params.keys():
            setattr(self, item, urllib.unquote_plus(params[item]))

    def parse_params(self, params):
        for item in params.keys():
            setattr(self, item, urllib.unquote_plus(params[item]))

    def get_live_title(self):
        if self.home and self.away:
            return '[COLOR green][LIVE NOW][/COLOR] {0} v {1}'.format(
                self.home, self.away)

    def get_airtime(self):
        try:
            delta = ((time.mktime(time.localtime()) -
                     time.mktime(time.gmtime())) / 3600)
            if time.localtime().tm_isdst:
                delta += 1
            ts_format = "%Y-%m-%dT%H:%M:%S+00:00"
            ts = datetime.datetime.fromtimestamp(
                time.mktime(time.strptime(self.start_date, ts_format)))
            ts += datetime.timedelta(hours=delta)
            return ts.strftime("%A %d %b @ %I:%M %p").replace(' 0', ' ')
        except OverflowError:
            return timestamp

    def make_time_string(self):
        try:
            timestamp = time.mktime(time.strptime(self.start_date,
                                                '%Y-%m-%dT%H:%M:%S+00:00'))
            video.date = datetime.date.fromtimestamp(timestamp)
        except Exception:
            pass

    def get_upcoming_title(self):
        if self.home and self.away:
            return '[COLOR red][Upcoming][/COLOR] {0} v {1} - {2}'.format(
                self.home, self.away, self.get_airtime())
