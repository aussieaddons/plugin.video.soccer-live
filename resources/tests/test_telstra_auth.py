from __future__ import absolute_import, unicode_literals

import io
import json
import os
try:
    import mock
except ImportError:
    import unittest.mock as mock

import responses

import testtools

import resources.lib.config as config
import resources.lib.telstra_auth as telstra_auth
from resources.tests.fakes import fakes


class TelstraAuthTests(testtools.TestCase):
    @classmethod
    def setUpClass(self):
        cwd = os.path.join(os.getcwd(), 'resources/tests')
        with open(os.path.join(cwd, 'fakes/json/ENTITLEMENTS.json'),
                  'rb') as f:
            self.ENTITLEMENTS_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/ENTITLEMENTS_ACTIVE.json'),
                  'rb') as f:
            self.ENTITLEMENTS_ACTIVE_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/MYID_TOKEN_RESP.json'),
                  'rb') as f:
            self.MYID_TOKEN_RESP_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/OAUTH.json'), 'rb') as f:
            self.OAUTH_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/SOCCER_TOKEN.json'),
                  'rb') as f:
            self.NRL_TOKEN_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/OFFERS_RESP.json'),
                  'rb') as f:
            self.OFFERS_RESP_JSON = io.BytesIO(f.read()).read()
        with open(
                os.path.join(cwd, 'fakes/json/OFFERS_FAIL_RESP.json'),
                'rb') as f:
            self.OFFERS_FAIL_RESP_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/ORDER_RESP.json'),
                  'rb') as f:
            self.ORDER_RESP_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/PURCHASE_RESP.json'),
                  'rb') as f:
            self.PURCHASE_RESP_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/STATUS_RESP.json'),
                  'rb') as f:
            self.STATUS_RESP_JSON = io.BytesIO(f.read()).read()
        with open(
                os.path.join(cwd, 'fakes/json/STATUS_FAIL_RESP.json'),
                'rb') as f:
            self.STATUS_FAIL_RESP_JSON = io.BytesIO(f.read()).read()
        with open(
                os.path.join(cwd, 'fakes/html/SPC_RESP.html'),
                'rb') as f:
            self.SPC_RESP_HTML = io.BytesIO(f.read()).read()
        with open(
                os.path.join(cwd, 'fakes/html/MYID_AUTH_RESP.html'),
                'rb') as f:
            self.MYID_AUTH_RESP_HTML = io.BytesIO(f.read()).read()
        with open(
                os.path.join(cwd, 'fakes/html/MYID_RESUME_AUTH_RESP.html'),
                'rb') as f:
            self.MYID_RESUME_AUTH_RESP_HTML = io.BytesIO(f.read()).read()


    @mock.patch.object(telstra_auth.TelstraAuth, '_get_aws_userid')
    @responses.activate
    def test_get_paid_token(self, mock_aws_userid):
        mock_aws_userid.side_effect = fakes.FAKE_UUID
        responses.add(responses.POST, config.OAUTH_URL,
                      body=self.OAUTH_JSON,
                      status=200)
        responses.add(responses.GET,
                      config.MEDIA_PURCHASE_URL.format(fakes.FAKE_UUID[0]),
                      body=self.PURCHASE_RESP_JSON,
                      status=200)
        responses.add(responses.GET, config.ENTITLEMENTS_URL,
                      body=self.ENTITLEMENTS_ACTIVE_JSON,
                      status=200)
        auth = telstra_auth.TelstraAuth('foo', 'bar')
        observed = auth.get_paid_token()
        self.assertEqual(json.dumps(
            {'pai': fakes.FAKE_UUID[0],
             'bearer': 'abc123'}),
            observed)

    @mock.patch.object(telstra_auth.TelstraAuth, '_get_aws_userid')
    @responses.activate
    def test_get_paid_token_fail_userpass(self, mock_aws_userid):
        responses.add(responses.POST, config.OAUTH_URL,
                      body=self.OAUTH_JSON,
                      status=200)
        mock_aws_userid.side_effect = telstra_auth.TelstraAuthException(
            'An error occurred (NotAuthorizedException) when calling the '
            'RespondToAuthChallenge operation: Incorrect username or '
            'password.')
        auth = telstra_auth.TelstraAuth('foo', 'wrongpassword')
        self.assertRaises(telstra_auth.TelstraAuthException,
                          auth.get_paid_token)

    @responses.activate
    @mock.patch('os.urandom')
    @mock.patch('uuid.uuid4')
    def test_get_free_token(self, mock_uuid, mock_random):
        mock_uuid.side_effect = fakes.FAKE_UUID
        mock_random.side_effect = fakes.FAKE_RANDOM
        responses.add(responses.POST, config.OAUTH_URL,
                      body=self.OAUTH_JSON,
                      status=200)
        responses.add(responses.GET, config.ENTITLEMENTS_URL,
                      body=self.ENTITLEMENTS_JSON,
                      status=200)
        responses.add(responses.GET,
                      config.SPC_URL.format(fakes.FAKE_UUID[1]),
                      body=self.SPC_RESP_HTML,
                      status=200)
        responses.add(responses.GET, config.MYID_AUTHORIZATION_URL,
                      body=self.MYID_AUTH_RESP_HTML,
                      status=200)
        responses.add(responses.POST,
                      config.MYID_RESUME_AUTHORIZATION_URL.format('ABCDE'),
                      body=self.MYID_RESUME_AUTH_RESP_HTML,
                      status=200)
        for url in config.SSO_SESSION_HANDLER_URLS:
            responses.add(responses.POST, url,
                          json={'status': 'success'},
                          status=200)

        responses.add(responses.GET,
                      '{0}{1}'.format(
                          config.MYID_RESUME_AUTHORIZATION_URL.format('ABCDE'),
                          '?ctfr-proceed=true'),
                      headers={'Set-Cookie': fakes.FAKE_BPSESSION_COOKIE,
                               'Location':
                                   fakes.MYID_RESUME_AUTH_REDIRECT_URL},
                      status=302)
        responses.add(responses.GET, fakes.MYID_RESUME_AUTH_REDIRECT_URL,
                      status=200)
        responses.add(responses.POST, config.MYID_TOKEN_URL,
                      body=self.MYID_TOKEN_RESP_JSON,
                      status=200)
        responses.add(responses.GET, config.OFFERS_URL,
                      body=self.OFFERS_RESP_JSON,
                      status=200)
        responses.add(responses.POST, config.MEDIA_ORDER_URL,
                      body=self.ORDER_RESP_JSON,
                      status=200)
        responses.add(responses.GET, config.ENTITLEMENTS_URL,
                      body=self.ENTITLEMENTS_ACTIVE_JSON,
                      status=200)
        auth = telstra_auth.TelstraAuth('foo', 'bar')
        observed = auth.get_free_token()
        self.assertEqual(json.dumps(
            {'pai': fakes.FAKE_UUID[0],
             'bearer': 'abc123'}),
            observed)

    @responses.activate
    @mock.patch('os.urandom')
    @mock.patch('uuid.uuid4')
    def test_get_free_token_fail_userpass(self, mock_uuid, mock_random):
        mock_uuid.side_effect = fakes.FAKE_UUID
        mock_random.side_effect = fakes.FAKE_RANDOM
        responses.add(responses.POST, config.OAUTH_URL,
                      body=self.OAUTH_JSON,
                      status=200)
        responses.add(responses.GET, config.ENTITLEMENTS_URL,
                      body=self.ENTITLEMENTS_JSON,
                      status=200)
        responses.add(responses.GET,
                      config.SPC_URL.format(fakes.FAKE_UUID[1]),
                      body=self.SPC_RESP_HTML,
                      status=200)
        responses.add(responses.GET, config.MYID_AUTHORIZATION_URL,
                      body=self.MYID_AUTH_RESP_HTML,
                      status=200)
        responses.add(responses.POST,
                      config.MYID_RESUME_AUTHORIZATION_URL.format('ABCDE'),
                      body=self.MYID_AUTH_RESP_HTML,
                      status=200)
        auth = telstra_auth.TelstraAuth('foo', 'wrongpassword')
        self.assertRaises(telstra_auth.TelstraAuthException,
                          auth.get_free_token)

    @responses.activate
    @mock.patch('os.urandom')
    @mock.patch('uuid.uuid4')
    def test_get_free_token_fail_no_offer(self, mock_uuid, mock_random):
        mock_uuid.side_effect = fakes.FAKE_UUID
        mock_random.side_effect = fakes.FAKE_RANDOM
        responses.add(responses.POST, config.OAUTH_URL,
                      body=self.OAUTH_JSON,
                      status=200)
        responses.add(responses.GET, config.ENTITLEMENTS_URL,
                      body=self.ENTITLEMENTS_JSON,
                      status=200)
        responses.add(responses.GET,
                      config.SPC_URL.format(fakes.FAKE_UUID[1]),
                      body=self.SPC_RESP_HTML,
                      status=200)
        responses.add(responses.GET, config.MYID_AUTHORIZATION_URL,
                      body=self.MYID_AUTH_RESP_HTML,
                      status=200)
        responses.add(responses.POST,
                      config.MYID_RESUME_AUTHORIZATION_URL.format('ABCDE'),
                      body=self.MYID_RESUME_AUTH_RESP_HTML,
                      status=200)
        for url in config.SSO_SESSION_HANDLER_URLS:
            responses.add(responses.POST, url,
                          json={'status': 'success'},
                          status=200)

        responses.add(responses.GET,
                      '{0}{1}'.format(
                          config.MYID_RESUME_AUTHORIZATION_URL.format('ABCDE'),
                          '?ctfr-proceed=true'),
                      headers={'Set-Cookie': fakes.FAKE_BPSESSION_COOKIE,
                               'Location':
                                   fakes.MYID_RESUME_AUTH_REDIRECT_URL},
                      status=302)
        responses.add(responses.GET, fakes.MYID_RESUME_AUTH_REDIRECT_URL,
                      status=200)
        responses.add(responses.POST, config.MYID_TOKEN_URL,
                      body=self.MYID_TOKEN_RESP_JSON,
                      status=200)
        responses.add(responses.GET, config.OFFERS_URL,
                      body=self.OFFERS_FAIL_RESP_JSON,
                      status=200)
        auth = telstra_auth.TelstraAuth('foo', 'bar')
        self.assertRaises(telstra_auth.TelstraAuthException,
                          auth.get_free_token)

    @responses.activate
    @mock.patch('os.urandom')
    @mock.patch('uuid.uuid4')
    def test_get_free_token_fail_no_eligible(self, mock_uuid, mock_random):
        mock_uuid.side_effect = fakes.FAKE_UUID
        mock_random.side_effect = fakes.FAKE_RANDOM
        responses.add(responses.POST, config.OAUTH_URL,
                      body=self.OAUTH_JSON,
                      status=200)
        responses.add(responses.GET, config.ENTITLEMENTS_URL,
                      body=self.ENTITLEMENTS_JSON,
                      status=200)
        responses.add(responses.GET,
                      config.SPC_URL.format(fakes.FAKE_UUID[1]),
                      body=self.SPC_RESP_HTML,
                      status=200)
        responses.add(responses.GET, config.MYID_AUTHORIZATION_URL,
                      body=self.MYID_AUTH_RESP_HTML,
                      status=200)
        responses.add(responses.POST,
                      config.MYID_RESUME_AUTHORIZATION_URL.format('ABCDE'),
                      body=self.MYID_RESUME_AUTH_RESP_HTML,
                      status=200)
        for url in config.SSO_SESSION_HANDLER_URLS:
            responses.add(responses.POST, url,
                          json={'status': 'success'},
                          status=200)

        responses.add(responses.GET,
                      '{0}{1}'.format(
                          config.MYID_RESUME_AUTHORIZATION_URL.format('ABCDE'),
                          '?ctfr-proceed=true'),
                      headers={'Set-Cookie': fakes.FAKE_BPSESSION_COOKIE,
                               'Location':
                                   fakes.MYID_RESUME_AUTH_REDIRECT_URL},
                      status=302)
        responses.add(responses.GET, fakes.MYID_RESUME_AUTH_REDIRECT_URL,
                      status=200)
        responses.add(responses.POST, config.MYID_TOKEN_URL,
                      body=self.MYID_TOKEN_RESP_JSON,
                      status=200)
        responses.add(responses.GET, config.OFFERS_URL,
                      json={'userMessage': 'No eligible services'},
                      status=404)
        auth = telstra_auth.TelstraAuth('foo', 'bar')
        self.assertRaises(telstra_auth.TelstraAuthException,
                          auth.get_free_token)

    @responses.activate
    @mock.patch('os.urandom')
    @mock.patch('uuid.uuid4')
    def test_get_free_token_fail_not_activated(self, mock_uuid, mock_random):
        mock_uuid.side_effect = fakes.FAKE_UUID
        mock_random.side_effect = fakes.FAKE_RANDOM
        responses.add(responses.POST, config.OAUTH_URL,
                      body=self.OAUTH_JSON,
                      status=200)
        responses.add(responses.GET, config.ENTITLEMENTS_URL,
                      body=self.ENTITLEMENTS_JSON,
                      status=200)
        responses.add(responses.GET,
                      config.SPC_URL.format(fakes.FAKE_UUID[1]),
                      body=self.SPC_RESP_HTML,
                      status=200)
        responses.add(responses.GET, config.MYID_AUTHORIZATION_URL,
                      body=self.MYID_AUTH_RESP_HTML,
                      status=200)
        responses.add(responses.POST,
                      config.MYID_RESUME_AUTHORIZATION_URL.format('ABCDE'),
                      body=self.MYID_RESUME_AUTH_RESP_HTML,
                      status=200)
        for url in config.SSO_SESSION_HANDLER_URLS:
            responses.add(responses.POST, url,
                          json={'status': 'success'},
                          status=200)

        responses.add(responses.GET,
                      '{0}{1}'.format(
                          config.MYID_RESUME_AUTHORIZATION_URL.format('ABCDE'),
                          '?ctfr-proceed=true'),
                      headers={'Set-Cookie': fakes.FAKE_BPSESSION_COOKIE,
                               'Location':
                                   fakes.MYID_RESUME_AUTH_REDIRECT_URL},
                      status=302)
        responses.add(responses.GET, fakes.MYID_RESUME_AUTH_REDIRECT_URL,
                      status=200)
        responses.add(responses.POST, config.MYID_TOKEN_URL,
                      body=self.MYID_TOKEN_RESP_JSON,
                      status=200)
        responses.add(responses.GET, config.OFFERS_URL,
                      body=self.OFFERS_RESP_JSON,
                      status=200)
        responses.add(responses.POST, config.MEDIA_ORDER_URL,
                      body=self.ORDER_RESP_JSON,
                      status=200)
        auth = telstra_auth.TelstraAuth('foo', 'bar')
        self.assertRaises(telstra_auth.TelstraAuthException,
                          auth.get_free_token)

    @mock.patch('uuid.uuid4')
    @responses.activate
    def test_get_mobile_token(self, mock_uuid):
        mock_uuid.side_effect = fakes.FAKE_UUID
        responses.add(responses.POST, config.OAUTH_URL,
                      body=self.OAUTH_JSON,
                      status=200)
        responses.add(responses.GET, config.MOBILE_ID_URL,
                      headers={'Set-Cookie': fakes.FAKE_MOBILE_COOKIE},
                      status=200)
        responses.add(responses.POST, config.MOBILE_OAUTH_URL,
                      body=self.NRL_TOKEN_JSON,
                      status=200)
        responses.add(responses.GET, config.OFFERS_URL,
                      body=self.OFFERS_RESP_JSON,
                      status=200)
        responses.add(responses.POST, config.MEDIA_ORDER_URL,
                      body=self.ORDER_RESP_JSON,
                      status=200)
        responses.add(responses.GET, config.ENTITLEMENTS_URL,
                      body=self.ENTITLEMENTS_ACTIVE_JSON,
                      status=200)
        auth = telstra_auth.TelstraAuth()
        observed = auth.get_mobile_token()
        self.assertEqual(json.dumps(
            {'pai': fakes.FAKE_UUID[0],
             'bearer': 'abc123'}),
            observed)

    @responses.activate
    def test_get_mobile_token_fail_no_mobile_data(self):
        responses.add(responses.POST, config.OAUTH_URL,
                      body=self.OAUTH_JSON,
                      status=200)
        responses.add(responses.GET, config.MOBILE_ID_URL,
                      headers={'Set-Cookie': fakes.FAKE_MOBILE_COOKIE_NO_DATA},
                      status=204)
        auth = telstra_auth.TelstraAuth()
        self.assertRaises(telstra_auth.TelstraAuthException,
                          auth.get_mobile_token)

    @responses.activate
    def test_get_mobile_token_fail_no_offer(self):
        responses.add(responses.POST, config.OAUTH_URL,
                      body=self.OAUTH_JSON,
                      status=200)
        responses.add(responses.GET, config.MOBILE_ID_URL,
                      headers={'Set-Cookie': fakes.FAKE_MOBILE_COOKIE},
                      status=200)
        responses.add(responses.POST, config.MOBILE_OAUTH_URL,
                      body=self.NRL_TOKEN_JSON,
                      status=200)
        responses.add(responses.GET, config.OFFERS_URL,
                      body=self.OFFERS_FAIL_RESP_JSON,
                      status=200)
        auth = telstra_auth.TelstraAuth()
        self.assertRaises(telstra_auth.TelstraAuthException,
                          auth.get_mobile_token)

    @responses.activate
    def test_get_mobile_token_fail_no_eligible(self):
        responses.add(responses.POST, config.OAUTH_URL,
                      body=self.OAUTH_JSON,
                      status=200)
        responses.add(responses.GET, config.MOBILE_ID_URL,
                      headers={'Set-Cookie': fakes.FAKE_MOBILE_COOKIE},
                      status=200)
        responses.add(responses.POST, config.MOBILE_OAUTH_URL,
                      body=self.NRL_TOKEN_JSON,
                      status=200)
        responses.add(responses.GET, config.OFFERS_URL,
                      json={'userMessage': 'No eligible services'},
                      status=404)
        auth = telstra_auth.TelstraAuth()
        self.assertRaises(telstra_auth.TelstraAuthException,
                          auth.get_mobile_token)

    @responses.activate
    def test_get_mobile_token_fail_activation(self):
        responses.add(responses.POST, config.OAUTH_URL,
                      body=self.OAUTH_JSON,
                      status=200)
        responses.add(responses.GET, config.MOBILE_ID_URL,
                      headers={'Set-Cookie': fakes.FAKE_MOBILE_COOKIE},
                      status=200)
        responses.add(responses.POST, config.MOBILE_OAUTH_URL,
                      body=self.NRL_TOKEN_JSON,
                      status=200)
        responses.add(responses.GET, config.OFFERS_URL,
                      body=self.OFFERS_RESP_JSON,
                      status=200)
        responses.add(responses.POST, config.MEDIA_ORDER_URL,
                      body=self.ORDER_RESP_JSON,
                      status=200)
        responses.add(responses.GET, config.ENTITLEMENTS_URL,
                      body=self.ENTITLEMENTS_JSON,
                      status=200)
        auth = telstra_auth.TelstraAuth()
        self.assertRaises(telstra_auth.TelstraAuthException,
                          auth.get_mobile_token)
