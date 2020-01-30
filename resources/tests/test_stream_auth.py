from __future__ import absolute_import, unicode_literals

import io
import os
try:
    import mock
except ImportError:
    import unittest.mock as mock

import responses

import testtools

import resources.lib.config as config
import resources.lib.stream_auth as stream_auth


class StreamAuthTests(testtools.TestCase):
    @classmethod
    def setUpClass(self):
        cwd = os.path.join(os.getcwd(), 'resources/tests')
        with open(os.path.join(cwd, 'fakes/xml/EMBED_TOKEN.xml'),
                  'rb') as f:
            self.EMBED_TOKEN_XML = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/xml/EMBED_TOKEN_FAIL.xml'),
                  'rb') as f:
            self.EMBED_TOKEN_FAIL_XML = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/AUTH.json'),
                  'rb') as f:
            self.AUTH_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/AUTH_FAILED.json'),
                  'rb') as f:
            self.AUTH_FAILED_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/MEDIA_AUTH.json'),
                  'rb') as f:
            self.MEDIA_AUTH_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/MEDIA_AUTH_EXPIRED.json'),
                  'rb') as f:
            self.MEDIA_AUTH_EXPIRED_JSON = io.BytesIO(f.read()).read()

    @mock.patch('resources.lib.stream_auth.cache.delete')
    def test_clear_ticket(self, mock_delete):
        stream_auth.clear_ticket()
        mock_delete.assert_called_with('SOCCERTICKET')

    @mock.patch('resources.lib.stream_auth.cache.get')
    def test_get_user_ticket_cached(self, mock_ticket):
        mock_ticket.return_value = 'foobar123456'
        observed = stream_auth.get_user_ticket()
        self.assertEqual('foobar123456', observed)

    @mock.patch(
        'resources.lib.stream_auth.telstra_auth.TelstraAuth.get_free_token')
    @mock.patch('resources.lib.stream_auth.addon.getSetting')
    @mock.patch('resources.lib.stream_auth.cache.get')
    def test_get_user_ticket_free(self, mock_ticket, mock_sub_type,
                                  mock_token):
        mock_ticket.return_value = ''
        mock_sub_type.return_value = '0'
        mock_token.return_value = 'foobar456789'

    @mock.patch(
        'resources.lib.stream_auth.telstra_auth.TelstraAuth.get_mobile_token')
    @mock.patch('resources.lib.stream_auth.addon.getSetting')
    @mock.patch('resources.lib.stream_auth.cache.get')
    def test_get_user_ticket_mobile(self, mock_ticket, mock_sub_type,
                                    mock_token):
        mock_ticket.return_value = ''
        mock_sub_type.return_value = '1'
        mock_token.return_value = 'foobar654321'
        observed = stream_auth.get_user_ticket()
        self.assertEqual('foobar654321', observed)

    @mock.patch(
        'resources.lib.stream_auth.telstra_auth.TelstraAuth.get_paid_token')
    @mock.patch('resources.lib.stream_auth.addon.getSetting')
    @mock.patch('resources.lib.stream_auth.cache.get')
    def test_get_user_ticket_paid(self, mock_ticket, mock_sub_type,
                                  mock_token):
        mock_ticket.return_value = ''
        mock_sub_type.return_value = '2'
        mock_token.return_value = 'foobar987654'
        observed = stream_auth.get_user_ticket()
        self.assertEqual('foobar987654', observed)

    @responses.activate
    def test_get_media_auth_token(self):
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, config.MEDIA_AUTH_URL.format(code='foo',
                                                                 pai='uuid'),
                     body=self.MEDIA_AUTH_JSON, status=200)
            observed = stream_auth.get_media_auth_token(
                'uuid', 'bearer', 'foo')
            self.assertEqual('token123', observed)

    @responses.activate
    @mock.patch('xbmc.log')
    @mock.patch('resources.lib.stream_auth.cache.delete')
    def test_get_embed_token_fail_401(self, mock_delete, mock_log):
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, config.MEDIA_AUTH_URL.format(code='foo',
                                                                 pai='uuid'),
                     body=self.MEDIA_AUTH_EXPIRED_JSON, status=401)
            self.assertRaises(stream_auth.AussieAddonsException,
                              stream_auth.get_media_auth_token,
                              'uuid', 'bearer', 'foo')
            mock_delete.assert_called_with('SOCCERTICKET')
            self.assertIn('Access Token expired', mock_log.call_args[0][0])
