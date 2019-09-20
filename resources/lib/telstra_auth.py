import base64
import binascii
import config
import hashlib
import json
import os
import random
import re
import urlparse
import uuid

from future.moves.urllib.parse import parse_qsl, urlparse, urlsplit

import requests

import xbmcgui

try:
    import boto3
    from warrant.aws_srp import AWSSRP
except ImportError:
    pass

from aussieaddonscommon.exceptions import AussieAddonsException
from aussieaddonscommon import session as custom_session
from aussieaddonscommon import utils


class TelstraAuthException(AussieAddonsException):
    """Telstra Auth exception
    This exception can be thrown with the reportable arg set which can
    determine whether or not it is allowed to be sent as an automatic
    error report
    """
    pass


class TelstraAuth(object):
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        self.session = custom_session.Session(force_tlsv1=False)
        self.prog_dialog = xbmcgui.DialogProgress()

    def get_code_verifier(self):
        letters = 'abcdef0123456789'
        verifier = ''.join(random.choice(letters) for i in range(64))
        return verifier.encode('utf-8')

    def get_code_challenge(self, verifier):
        code_challenge_digest = hashlib.sha256(verifier).digest()
        code_challenge = base64.b64encode(code_challenge_digest, b'-_').rstrip(
            b'=')
        return code_challenge

    def create_dialog(self, msg):
        self.prog_dialog.create(msg)

    def get_paid_token(self):
        session = custom_session.Session(force_tlsv1=False)
        prog_dialog = xbmcgui.DialogProgress()
        prog_dialog.create('Logging in with mobile service')
        prog_dialog.update(1, 'Obtaining user ID from AWS')
        try:
            client = boto3.client('cognito-idp',
                                  region_name=config.AWS_REGION,
                                  aws_access_key_id='',
                                  aws_secret_access_key='')
            aws = AWSSRP(username=self.username,
                         password=self.password,
                         pool_id=config.AWS_POOL_ID,
                         client_id=config.AWS_CLIENT_ID,
                         client=client)
        except NameError:
            raise TelstraAuthException('Paid subscriptions not supported on some '
                                       'platforms of Kodi < 18. Please upgrade to '
                                       'Kodi 18 to resolve this.')
        try:
            tokens = aws.authenticate_user().get('AuthenticationResult')
        except Exception as e:
            raise TelstraAuthException(str(e))

        response = client.get_user(AccessToken=tokens.get('AccessToken'))
        userid = response.get('Username')

        prog_dialog.update(33, 'Obtaining oauth token')
        config.OAUTH_DATA.update({'x-user-id': userid})
        oauth_resp = session.post(config.OAUTH_URL,
                                  data=config.OAUTH_DATA)
        oauth_json = json.loads(oauth_resp.text)
        access_token = oauth_json.get('access_token')
        session.headers = {}
        session.headers.update(
            {'Authorization': 'Bearer {0}'.format(access_token)})

        prog_dialog.update(66, 'Checking for valid subscription')
        try:
            session.get(config.MEDIA_PURCHASE_URL.format(userid))

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                message = json.loads(e.response.text).get('message')
                raise TelstraAuthException(message)
            else:
                utils.log(json.loads(e.response.text).get('exception'))
                raise TelstraAuthException('Unknown error. Please check the log '
                                           'for more information.')
        session.close()
        prog_dialog.update(100, 'Finished!')
        prog_dialog.close()
        return json.dumps({'pai': str(userid), 'bearer': access_token})

    def set_initial_token(self):
        # Send our first login request to Yinzcam, recieve (unactivated) ticket

        self.userid = uuid.uuid4()
        config.OAUTH_DATA.update({'x-user-id': self.userid})
        oauth_resp = self.session.post(config.OAUTH_URL,
                                  data=config.OAUTH_DATA)
        oauth_json = json.loads(oauth_resp.text)
        self.access_token = oauth_json.get('access_token')
        self.session.headers = {}
        self.session.headers.update(
            {'Authorization': 'Bearer {0}'.format(self.access_token)})

    def set_sso_client_id(self):
        """
        GET to our spc url and receive SSO client ID
        :return:
        """
        self.session.headers = config.SPC_HEADERS
        spc_resp = self.session.get(config.SPC_URL)
        sso_token_match = re.search('ssoClientId = "(\\w+)"', spc_resp.text)
        try:
            self.sso_client_id = sso_token_match.group(1)
        except AttributeError as e:
            utils.log('SPC login response: {0}'.format(spc_resp.text))
            raise e


    def set_identity_path_token(self):
        self.code_verifier = self.get_code_verifier()
        myid_oauth_params = dict(config.MYID_AUTH_PARAMS)
        myid_oauth_params.update({'client_id': self.sso_client_id,
                                  'state': binascii.b2a_hex(os.urandom(16)),
                                  'code_challenge': self.get_code_challenge(
                                      self.code_verifier)})
        myid_auth = self.session.get(config.MYID_AUTHORIZATION_URL,
                                     params=myid_oauth_params)

        identify_path_match = re.search('action="/identity/as/(\\w+)/',
                                        myid_auth.text)
        try:
            self.identify_path_token = identify_path_match.group(1)
        except AttributeError as e:
            raise e

    def set_myid_auth_resume_resp_text(self):
        myid_auth_resume_data = dict(config.MYID_AUTH_RESUME_DATA)
        myid_auth_resume_data.update(
            {'pf.username': self.username, 'pf.pass': self.password})
        myid_auth_resume = self.session.post(
            config.MYID_RESUME_AUTHORIZATION_URL.format(
                self.identify_path_token),
            data=myid_auth_resume_data)
        self.myid_auth_resume_resp_text = myid_auth_resume.text

    def validate_myid_auth(self):
        auth_page_title_match = re.search('<title>(.*?)</title>',
                                          self.myid_auth_resume_resp_text)
        try:
            auth_page_title = auth_page_title_match.group(1)
            if auth_page_title == 'Sign in to Telstra with your Telstra ID':
                raise TelstraAuthException(
                    'Invalid Telstra ID username or password')
        except AttributeError as e:
            raise e

    def signon_to_sso_sessions(self):
        sso_session_cookie = self.session.cookies.get_dict().get('SSOSession')
        for url in config.SSO_SESSION_HANDLER_URLS:
            self.session.post(url, data={'SSOCookie': sso_session_cookie})

    def set_callback_code(self):
        """
        get oauth code
        :return:
        """
        myid_signon_proceed = self.session.get(
            config.MYID_RESUME_AUTHORIZATION_URL.format(
                self.identify_path_token),
            params={'ctfr-proceed': 'true'})
        query = urlparse(myid_signon_proceed.url).query
        self.callback_code = dict(parse_qsl(query)).get('code')

    def set_bearer_token(self):
        """
        finally get access token
        :return:
        """
        token_params = dict(config.MYID_TOKEN_PARAMS)

        token_params.update({'client_id': self.sso_client_id,
                             'code': self.callback_code,
                             'code_verifier': self.code_verifier})
        token_resp = self.session.post(config.MYID_TOKEN_URL,
                                       data=token_params)
        self.bearer_token = json.loads(token_resp.text).get('access_token')

    def set_offers_resp(self):
        """
        First check if there are any eligible services attached to the
        account
        :return:
        """
        media_order_headers = config.MEDIA_ORDER_HEADERS

        media_order_headers.update(
            {'Authorization': 'Bearer {0}'.format(self.bearer_token)})
        self.session.headers = media_order_headers

        try:
            self.offers = self.session.get(config.OFFERS_URL)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                message = json.loads(e.response.text).get('userMessage')
                message += (' Please visit {0} '.format(config.HUB_URL) +
                            'for further instructions to link your mobile '
                            'service to the supplied Telstra ID')
                raise TelstraAuthException(message)
            else:
                raise TelstraAuthException(e)

    def set_ph_no_list(self):
        try:
            offer_data = json.loads(self.offers.text)
            offers_list = offer_data['data']['offers']
            self.ph_no_list = []

            for offer in offers_list:
                if offer.get('name') != 'NRL Live Pass':
                    continue
                data = offer.get('productOfferingAttributes')
                serv_id = \
                    [x['value'] for x in data if x['name'] == 'ServiceId'][0]
                self.ph_no_list.append(serv_id)

            if len(self.ph_no_list) == 0:
                raise TelstraAuthException(
                    'Unable to determine if you have any eligible services. '
                    'Please ensure there is an eligible service linked to '
                    'your Telstra ID to redeem the free offer. Please visit '
                    '{0} for further instructions'.format(config.HUB_URL))
        except Exception as e:
            raise e

    def _order(self, ph_no):
        try:
            order_data = config.MEDIA_ORDER_JSON.format(ph_no,
                                                        config.OFFER_ID,
                                                        self.userid)
            order = self.session.post(config.MEDIA_ORDER_URL,
                                      data=order_data)
            self.last_order_response = order
            # check to make sure order has been placed correctly
            if order.status_code == 201:
                try:
                    order_json = json.loads(order.text)
                    status = order_json['data'].get('status') == 'COMPLETE'
                    if status:
                        utils.log('Order status complete')
                        return True
                except Exception:
                    utils.log(
                        'Unable to check status of order, continuing')
        except requests.exceptions.HTTPError as e:
            utils.log(
                'Error {0} on order post'.format(e.response.status_code))
            self.last_order_response = e.response

    def order_subscription(self):
        """
        'Order' the subscription package to activate the service
        :return:
        """
        for ph_no in self.ph_no_list:
            if self._order(ph_no):
                break

        if str(self.last_order_response.status_code)[0] != '2':
            self.last_order_response.raise_for_status()

    def confirm_activation(self):
        self.session.headers = {}
        self.session.headers.update(
            {'Authorization': 'Bearer {0}'.format(self.bearer_token)})
        confirm = json.loads(self.session.get(config.ENTITLEMENTS_URL).text)
        if len(confirm.get('entitlements')) < 1:
            raise AussieAddonsException('Telstra ID activation failed')

    def get_free_token(self):
        """
        Obtain a valid token from Telstra/Yinzcam, will be used to make
        requests for Ooyala embed tokens
        """
        self.create_dialog('Activating live pass via free offer')
        self.prog_dialog.update(1, 'Obtaining oauth token')
        self.set_initial_token()

        # Check entitlements (not sure if needed)
        self.session.get(config.ENTITLEMENTS_URL)

        self.prog_dialog.update(16, 'Getting SSO Client ID')

        self.set_sso_client_id()
        self.prog_dialog.update(40,
                                'Signing in with Telstra ID username/password')
        self.set_identity_path_token()
        self.set_myid_auth_resume_resp_text()
        self.validate_myid_auth()
        self.signon_to_sso_sessions()

        self.prog_dialog.update(50, 'Getting OAuth access token')
        self.set_callback_code()
        self.set_bearer_token()

        self.prog_dialog.update(60, 'Determining eligible services')
        self.set_offers_resp()
        self.set_ph_no_list()

        self.prog_dialog.update(80, 'Activating live pass on service')
        self.order_subscription()

        self.prog_dialog.update(83, 'Confirming activation')
        self.confirm_activation()

        self.session.close()
        self.prog_dialog.update(100, 'Finished!')
        self.prog_dialog.close()
        return json.dumps({'pai': str(self.userid), 'bearer': self.access_token})

    # Mobile
    def set_mobile_id(self):
        mobile_userid_resp = self.session.get(config.MOBILE_ID_URL)
        mobile_userid_cookies = mobile_userid_resp.cookies.get_dict()
        self.mobile_userid = mobile_userid_cookies.get('GUID_S')
        if not self.mobile_userid or mobile_userid_cookies.get('nouid'):
            raise TelstraAuthException(
                'Not connected to Telstra Mobile network. '
                'Please disable WiFi and enable mobile '
                'data if on a Telstra mobile device, or '
                "connect this device's WiFi to a device "
                'that is on the Telstra Mobile network '
                'and try again.')

    def set_mobile_bearer_token(self):
        data = config.MOBILE_TOKEN_PARAMS
        data.update({'x-user-id': self.mobile_userid})
        mobile_token_resp = self.session.post(config.MOBILE_OAUTH_URL,
                                              data=data)
        self.bearer_token = json.loads(mobile_token_resp.text).get(
            'access_token')

    def get_mobile_token(self):
        self.create_dialog('Activating live pass via mobile network')
        self.prog_dialog.update(1, 'Obtaining oauth token')
        self.set_initial_token()
        # remove auth header, not wanted for some reason...
        self.session.headers.pop('Authorization')

        self.prog_dialog.update(20, 'Obtaining mobile token')
        self.set_mobile_id()
        self.set_mobile_bearer_token()

        self.prog_dialog.update(60, 'Determining eligible services')
        self.set_offers_resp()
        self.set_ph_no_list()

        self.prog_dialog.update(80, 'Activating live pass on service')
        self.order_subscription()

        self.prog_dialog.update(83, 'Confirming activation')
        self.confirm_activation()


        self.session.close()
        self.prog_dialog.update(100, 'Finished!')
        self.prog_dialog.close()
        return json.dumps({'pai': str(self.userid), 'bearer': self.access_token})
