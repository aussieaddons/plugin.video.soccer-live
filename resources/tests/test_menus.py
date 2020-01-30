from __future__ import absolute_import, unicode_literals

import datetime
import io
import os
import sys

try:
    import mock
except ImportError:
    import unittest.mock as mock

from future.moves.urllib.parse import parse_qsl

import responses

import testtools

import resources.lib.config as config
from resources.tests.fakes import fakes

#  https://blog.xelnor.net/python-mocking-datetime/
real_datetime_class = datetime.datetime


def mock_datetime_now(target, dt):
    class DatetimeSubclassMeta(type):
        @classmethod
        def __instancecheck__(mcs, obj):
            return isinstance(obj, real_datetime_class)

    class BaseMockedDatetime(real_datetime_class):
        @classmethod
        def now(cls, tz=None):
            return target.replace(tzinfo=tz)

        @classmethod
        def utcnow(cls):
            return target

    MockedDatetime = DatetimeSubclassMeta(
        str('datetime'), (BaseMockedDatetime,), {})
    return mock.patch.object(dt, 'datetime', MockedDatetime)


class MenusTests(testtools.TestCase):

    @classmethod
    def setUpClass(self):
        cwd = os.path.join(os.getcwd(), 'resources/tests')
        with open(os.path.join(cwd, 'fakes/json/CONFIG.json'), 'rb') as f:
            self.CONFIG_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/HOME.json'), 'rb') as f:
            self.HOME_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/MATCHES_FIXTURE.json'),
                  'rb') as f:
            self.MATCHES_FIXTURE_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/MATCHES_SUMMARY.json'),
                  'rb') as f:
            self.MATCHES_SUMMARY_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/VIDEOS.json'), 'rb') as f:
            self.VIDEOS_JSON = io.BytesIO(f.read()).read()

    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.soccer-live/', '2', '',
                 'resume:false'])
    @responses.activate
    def test_make_comp_list(self, mock_listitem):
        mock_listitem.side_effect = fakes.FakeListItem
        mock_plugin = fakes.FakePlugin()
        responses.add('GET', config.CONFIG_URL,
                      self.CONFIG_JSON, status=200)
        with mock.patch.dict('sys.modules', xbmcplugin=mock_plugin):
            import resources.lib.menus as menus
            menus.make_comp_list({})
            expected_title = 'Hyundai A-League'
            expected = fakes.FakeListItem(expected_title)
            expected.setThumbnailImage('example.jpg')
            expected.setIconImage('example.jpg')
            expected.setInfo('video', {'plot': expected_title,
                                       'plotoutline': expected_title})
            expected.setProperty('IsPlayable', 'false')

            for attrib in vars(mock_plugin.directory[0].get('listitem')):
                self.assertEqual(getattr(expected, attrib),
                                 getattr(mock_plugin.directory[0].get(
                                     'listitem'), attrib))

    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.soccer-live/', '2',
                 'action=listrounds&active_season=2019&id=214&rnd=9&tag'
                 '=aleague&thumb=https%3a%2f%2fwww.myfootball.com.au%2fsites'
                 '%2fdefault%2ffiles%2fstyles%2fimage_1200x%2fpublic%2f2017'
                 '-09%2faleague-visit.png%3fitok%3d-GzwbJES&title=Round%2016',
                 'resume:false'])
    @responses.activate
    def test_make_replay_list(self, mock_listitem):
        params = dict(parse_qsl(sys.argv[2][1:]))
        mock_listitem.side_effect = fakes.FakeListItem
        mock_plugin = fakes.FakePlugin()
        query = 'c{0}/s{1}/r{2}/fixture'.format(params.get('id'),
                                                params.get('active_season'),
                                                params.get('rnd'))
        responses.add('GET', config.MATCHES_URL.format(query),
                      self.MATCHES_FIXTURE_JSON, status=200)
        with mock.patch.dict('sys.modules', xbmcplugin=mock_plugin):
            import resources.lib.menus as menus

            menus.make_replay_list(params)
            self.assertIn('Melbourne City FC vs',
                          mock_plugin.directory[0].get('listitem').getLabel())

    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.soccer-live/', '2',
                 '?action=listcomps&active_season=2019&id=214&tag=aleague'
                 '&thumb=https%3a%2f%2fwww.myfootball.com.au%2fsites'
                 '%2fdefault%2ffiles%2fstyles%2fimage_1200x%2fpublic%2f2017'
                 '-09%2faleague-visit.png%3fitok%3d-GzwbJES&title=Hyundai'
                 '%20A-League&type=competition',
                 'resume:false'])
    @responses.activate
    def test_make_round_list(self, mock_listitem):
        params = dict(parse_qsl(sys.argv[2][1:]))
        mock_listitem.side_effect = fakes.FakeListItem
        mock_plugin = fakes.FakePlugin()
        query = 'c{0}/s{1}/summary'.format(params.get('id'),
                                           params.get('active_season'))
        responses.add('GET', config.MATCHES_URL.format(query),
                      self.MATCHES_SUMMARY_JSON, status=200)
        with mock.patch.dict('sys.modules', xbmcplugin=mock_plugin):
            import resources.lib.menus as menus
            menus.make_round_list(params)
            self.assertEqual(16, len(mock_plugin.directory))

    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.soccer-live/', '2',
                 '?action=listcategories&category=Videos',
                 'resume:false'])
    @responses.activate
    def test_make_video_list(self, mock_listitem):
        params = dict(parse_qsl(sys.argv[2][1:]))
        mock_listitem.side_effect = fakes.FakeListItem
        mock_plugin = fakes.FakePlugin()
        responses.add('GET', config.VIDEOS_URL,
                      self.VIDEOS_JSON, status=200)
        with mock.patch.dict('sys.modules', xbmcplugin=mock_plugin):
            import resources.lib.menus as menus
            menus.make_video_list(params)
            self.assertEqual(50, len(mock_plugin.directory))
            self.assertIn('GOAL OF ROUND 16',
                          mock_plugin.directory[1].get('listitem').getLabel())

    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.soccer-live/', '2',
                 '?action=listcategories&category=Videos',
                 'resume:false'])
    @responses.activate
    def test_make_live_list(self, mock_listitem):
        params = dict(parse_qsl(sys.argv[2][1:]))
        mock_listitem.side_effect = fakes.FakeListItem
        mock_plugin = fakes.FakePlugin()
        responses.add('GET', config.HOME_URL,
                      self.HOME_JSON, status=200)
        with mock.patch.dict('sys.modules', xbmcplugin=mock_plugin):
            import resources.lib.menus as menus
            with mock_datetime_now(datetime.datetime(2020, 1, 25), datetime):
                menus.make_live_list(params)
                self.assertEqual(2, len(mock_plugin.directory))
                self.assertIn('Upcoming', mock_plugin.directory[1].get(
                    'listitem').getLabel())
