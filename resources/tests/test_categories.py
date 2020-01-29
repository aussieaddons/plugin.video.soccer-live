from __future__ import absolute_import, unicode_literals

import io
import os

try:
    import mock
except ImportError:
    import unittest.mock as mock

from future.moves.urllib.parse import parse_qsl, unquote_plus, \
    urlencode, urlparse

import testtools

import resources.lib.config as config
from resources.tests.fakes import fakes


class MenusTests(testtools.TestCase):

    @classmethod
    def setUpClass(self):
        cwd = os.path.join(os.getcwd(), 'resources/tests')
        with open(os.path.join(cwd, 'fakes/json/CONFIG.json'), 'rb') as f:
            self.CONFIG_JSON = io.BytesIO(f.read()).read()

    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.soccer-live/', '2', '', 'resume:false'])
    def test_list_categories(self, mock_listitem):
        mock_listitem.side_effect = fakes.FakeListItem
        mock_plugin = fakes.FakePlugin()
        with mock.patch.dict('sys.modules', xbmcplugin=mock_plugin):
            import resources.lib.categories as categories
            categories.list_categories()
            for index, category in enumerate(config.CATEGORIES):
                expected_url = 'plugin://{addonid}/?{params}'.format(
                    addonid=config.ADDON_ID,
                    params=unquote_plus(urlencode({'action': 'listcategories',
                                                   'category': category})))
                observed_url = mock_plugin.directory[index].get('url')
                expected = urlparse(expected_url)
                observed = urlparse(observed_url)
                for x in range(6):
                    if x == 4:
                        self.assertEqual(dict(parse_qsl(expected[x])),
                                         dict(parse_qsl(observed[x])))
                    else:
                        self.assertEqual(expected[x], observed[x])