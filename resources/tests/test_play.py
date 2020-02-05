from __future__ import absolute_import, unicode_literals

import io
import json
import os
import re
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


def escape_regex(s):
    escaped = re.escape(s)
    return escaped.replace('\\{', '{').replace('\\}', '}')


class PlayTests(testtools.TestCase):
    @classmethod
    def setUpClass(self):
        cwd = os.path.join(os.getcwd(), 'resources/tests')
        with open(os.path.join(cwd, 'fakes/json/BC_EDGE.json'), 'rb') as f:
            self.BC_EDGE_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/CONFIG.json'), 'rb') as f:
            self.CONFIG_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/MEDIA_AUTH.json'), 'rb') as f:
            self.MEDIA_AUTH_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/SIGN.json'), 'rb') as f:
            self.SIGN_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/xml/EMBED_TOKEN.xml'),
                  'rb') as f:
            self.EMBED_TOKEN_XML = io.BytesIO(f.read()).read()

    @responses.activate
    @mock.patch('resources.lib.stream_auth.cache.get')
    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.soccer-live/',
                 '2',
                 '?action=listreplays&desc=Wellington+Phoenix+vs+Newcastle'
                 '+Jets%2C+Hyundai+A-League%2C+Round+16%2C+24th+Jan+2020'
                 '&premium=True&tag=aleague&thumb=https%3A%2F%2Fwww'
                 '.myfootball.com.au%2Fsites%2Fdefault%2Ffiles%2Fstyles'
                 '%2Fimage_1200x%2Fpublic%2F2017-09%2Faleague-visit.png'
                 '%3Fitok%3D-GzwbJES&title=Wellington+Phoenix+vs+Newcastle'
                 '+Jets%2C+Hyundai+A-League%2C+Round+16%2C+24th+Jan+2020'
                 '&video_id=6126203404001'])
    def test_play_video(self, mock_listitem, mock_ticket):
        params = dict(parse_qsl(sys.argv[2][1:]))
        escaped_auth_url = re.escape(
            config.SIGN_URL).replace('\\{', '{').replace('\\}', '}')
        auth_url = re.compile(escaped_auth_url.format('.*', '.*', '.*'))
        responses.add(responses.GET, auth_url,
                      body=self.SIGN_JSON, status=200)
        responses.add(responses.GET,
                      config.MEDIA_AUTH_URL.format(code=params.get('video_id'),
                                                   pai=fakes.FAKE_UUID[0]),
                      body=self.MEDIA_AUTH_JSON, status=200)
        escaped_bc_url = re.escape(
            config.BC_URL).replace('\\{', '{').replace('\\}', '}')
        bc_url = re.compile(escaped_bc_url.format('.*', '.*'))
        responses.add(responses.GET,
                      bc_url,
                      body=self.BC_EDGE_JSON, status=200)
        responses.add(responses.GET, config.CONFIG_URL,
                      body=self.CONFIG_JSON, status=200)
        mock_ticket.return_value = json.dumps({'pai': fakes.FAKE_UUID[0],
                                               'bearer': 'abc123'})
        mock_listitem.side_effect = fakes.FakeListItem

        mock_plugin = fakes.FakePlugin()
        with mock.patch.dict('sys.modules', xbmcplugin=mock_plugin):
            import resources.lib.play as play
            play.play_video(params)
            self.assertEqual('https://foo.com/index.m3u8',
                             mock_plugin.resolved[2].getPath())
