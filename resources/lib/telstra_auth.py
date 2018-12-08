import binascii
import config
import json
import os
import re
import requests
import urlparse
import uuid
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


def get_paid_token(username, password):
    session = custom_session.Session(force_tlsv1=False)
    prog_dialog = xbmcgui.DialogProgress()
    prog_dialog.create('Logging in with mobile service')
    prog_dialog.update(1, 'Obtaining user ID from AWS')
    try:
        client = boto3.client('cognito-idp',
                              region_name=config.AWS_REGION,
                              aws_access_key_id='',
                              aws_secret_access_key='')
        aws = AWSSRP(username=username,
                     password=password,
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

    prog_dialog.update(20, 'Obtaining oauth token')
    config.OAUTH_DATA.update({'x-user-id': userid})
    oauth_resp = session.post(config.OAUTH_URL,
                              data=config.OAUTH_DATA)
    oauth_json = json.loads(oauth_resp.text)
    access_token = oauth_json.get('access_token')
    session.headers = {}
    session.headers.update(
        {'Authorization': 'Bearer {0}'.format(access_token)})

    prog_dialog.update(40, 'Checking for valid subscription')
    try:
        purchase_resp = session.get(config.MEDIA_PURCHASE_URL.format(userid))

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


def get_mobile_token():
    session = custom_session.Session(force_tlsv1=False)
    prog_dialog = xbmcgui.DialogProgress()
    prog_dialog.create('Logging in with mobile service')
    prog_dialog.update(1, 'Obtaining oauth token')

    userid = uuid.uuid4()
    data = config.MOBILE_TOKEN_PARAMS.update({'x-user-id': userid})
    mobile_token_resp = session.post(config.MOBILE_TOKEN_URL, data=data)
    bearer_token = json.loads(mobile_token_resp.text).get('access_token')

    # First check if there are any eligible services attached to the account
    prog_dialog.update(50, 'Determining eligible services')
    offer_id = dict(urlparse.parse_qsl(
                    urlparse.urlsplit(spc_url)[3]))['offerId']
    media_order_headers = config.MEDIA_ORDER_HEADERS
    media_order_headers.update(
        {'Authorization': 'Bearer {0}'.format(bearer_token)})
    session.headers = media_order_headers
    try:
        offers = session.get(config.OFFERS_URL)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            message = json.loads(e.response.text).get('userMessage')
            message += (' Please visit {0} '.format(config.HUB_URL) +
                        'for further instructions to link your mobile '
                        'service to the supplied Telstra ID')
            raise TelstraAuthException(message)
        else:
            raise TelstraAuthException(e.response.status_code)
    try:
        offer_data = json.loads(offers.text)
        offers_list = offer_data['data']['offers']
        ph_no = None
        for offer in offers_list:
            if offer.get('name') != 'My Football Live Pass':
                continue
            data = offer.get('productOfferingAttributes')
            ph_no = [x['value'] for x in data if x['name'] == 'ServiceId'][0]
        if not ph_no:
            raise TelstraAuthException(
                'Unable to determine if you have any eligible services. '
                'Please ensure there is an eligible service linked to '
                'your Telstra ID to redeem the free offer. Please visit '
                '{0} for further instructions'.format(config.HUB_URL))
    except Exception as e:
        raise e

    # 'Order' the subscription package to activate the service
    prog_dialog.update(66, 'Activating live pass on service')
    order_data = config.MEDIA_ORDER_JSON.format(ph_no, offer_id, userid)
    order = session.post(config.MEDIA_ORDER_URL, data=order_data)

    # check to make sure order has been placed correctly
    if order.status_code == 201:
        try:
            order_json = json.loads(order.text)
            status = order_json['data'].get('status') == 'COMPLETE'
            if status:
                utils.log('Order status complete')
        except:
            utils.log('Unable to check status of order, continuing anyway')

    # Confirm activation
    prog_dialog.update(83, 'Confirming activation')
    session.headers = {}
    session.headers.update(
        {'Authorization': 'Bearer {0}'.format(access_token)})
    confirm = json.loads(session.get(config.ENTITLEMENTS_URL).text)
    if len(confirm.get('entitlements')) < 1:
        raise AussieAddonsException('Telstra ID activation failed')

    session.close()
    prog_dialog.update(100, 'Finished!')
    prog_dialog.close()
    return json.dumps({'pai': str(userid), 'bearer': access_token})


def get_free_token(username, password):
    """
    Obtain a valid token from Telstra/Yinzcam, will be used to make
    requests for Ooyala embed tokens
    """
    session = custom_session.Session(force_tlsv1=False)
    prog_dialog = xbmcgui.DialogProgress()
    prog_dialog.create('Logging in with Telstra ID')

    # Send our first login request to Yinzcam, recieve (unactivated) ticket
    prog_dialog.update(1, 'Obtaining oauth token')
    userid = uuid.uuid4()
    config.OAUTH_DATA.update({'x-user-id': userid})
    oauth_resp = session.post(config.OAUTH_URL,
                              data=config.OAUTH_DATA)
    oauth_json = json.loads(oauth_resp.text)
    access_token = oauth_json.get('access_token')
    session.headers = {}
    session.headers.update(
        {'Authorization': 'Bearer {0}'.format(access_token)})

    # Check entitlements (not sure if needed)
    session.get(config.ENTITLEMENTS_URL)

    prog_dialog.update(16, 'Getting SSO Client ID')
    # GET to our spc url and receive SSO client ID
    session.headers = config.SPC_HEADERS  # check if needed
    spc_url = config.SPC_URL.format(userid)
    spc_resp = session.get(spc_url)
    sso_token_match = re.search('ssoClientId = "(\w+)"', spc_resp.text)
    try:
        sso_token = sso_token_match.group(1)
    except AttributeError as e:
        utils.log('SPC login response: {0}'.format(spc_resp.text))
        raise e

    # Sign in to telstra.com with our SSO client id to get the url
    # for retrieving the bearer token for media orders
    prog_dialog.update(33, 'Signing on to telstra.com')
    sso_params = config.SSO_PARAMS
    sso_params.update({'client_id': sso_token,
                       'state': binascii.b2a_hex(os.urandom(16)),
                       'nonce': binascii.b2a_hex(os.urandom(16))})

    sso_auth_resp = session.get(config.SSO_URL, params=sso_params)
    sso_url = dict(urlparse.parse_qsl(
                   urlparse.urlsplit(sso_auth_resp.url)[3])).get('goto')

    # login to telstra.com.au and get our BPSESSION cookie
    session.headers.update(config.SIGNON_HEADERS)
    signon_data = config.SIGNON_DATA
    signon_data = {'username': username, 'password': password, 'goto': sso_url}
    signon = session.post(config.SIGNON_URL,
                          data=signon_data,
                          allow_redirects=False)
    bp_session = session.cookies.get_dict().get('BPSESSION')

    # check signon is valid (correct username/password)

    signon_pieces = urlparse.urlsplit(signon.headers.get('Location'))
    signon_query = dict(urlparse.parse_qsl(signon_pieces.query))

    utils.log('Sign-on result: %s' % signon_query)

    if 'errorcode' in signon_query:
        if signon_query['errorcode'] == '0':
            raise TelstraAuthException('Please enter your username '
                                       'in the settings')
        if signon_query['errorcode'] == '1':
            raise TelstraAuthException('Please enter your password '
                                       'in the settings')
        if signon_query['errorcode'] == '2':
            raise TelstraAuthException('Please enter your username and '
                                       'password in the settings')
        if signon_query['errorcode'] == '3':
            raise TelstraAuthException('Invalid Telstra ID username/password. '
                                       'Please check your username and '
                                       'password in the settings')

    # Use BPSESSION cookie to ask for bearer token
    sso_headers = config.SSO_HEADERS
    sso_headers.update({'Cookie': 'BPSESSION={0}'.format(bp_session)})
    session.headers = sso_headers
    sso_token_resp = session.get(sso_url)
    bearer_token = dict(urlparse.parse_qsl(
                    urlparse.urlsplit(sso_token_resp.url)[4]))['access_token']

    # First check if there are any eligible services attached to the account
    prog_dialog.update(50, 'Determining eligible services')
    offer_id = dict(urlparse.parse_qsl(
                    urlparse.urlsplit(spc_url)[3]))['offerId']
    media_order_headers = config.MEDIA_ORDER_HEADERS
    media_order_headers.update(
        {'Authorization': 'Bearer {0}'.format(bearer_token)})
    session.headers = media_order_headers
    try:
        offers = session.get(config.OFFERS_URL)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            message = json.loads(e.response.text).get('userMessage')
            message += (' Please visit {0} '.format(config.HUB_URL) +
                        'for further instructions to link your mobile '
                        'service to the supplied Telstra ID')
            raise TelstraAuthException(message)
        else:
            raise TelstraAuthException(e.response.status_code)
    try:
        offer_data = json.loads(offers.text)
        offers_list = offer_data['data']['offers']
        ph_no = None
        for offer in offers_list:
            if offer.get('name') != 'My Football Live Pass':
                continue
            data = offer.get('productOfferingAttributes')
            ph_no = [x['value'] for x in data if x['name'] == 'ServiceId'][0]
        if not ph_no:
            raise TelstraAuthException(
                'Unable to determine if you have any eligible services. '
                'Please ensure there is an eligible service linked to '
                'your Telstra ID to redeem the free offer. Please visit '
                '{0} for further instructions'.format(config.HUB_URL))
    except Exception as e:
        raise e

    # 'Order' the subscription package to activate the service
    prog_dialog.update(66, 'Activating live pass on service')
    order_data = config.MEDIA_ORDER_JSON.format(ph_no, offer_id, userid)
    order = session.post(config.MEDIA_ORDER_URL, data=order_data)

    # check to make sure order has been placed correctly
    if order.status_code == 201:
        try:
            order_json = json.loads(order.text)
            status = order_json['data'].get('status') == 'COMPLETE'
            if status:
                utils.log('Order status complete')
        except:
            utils.log('Unable to check status of order, continuing anyway')

    # Confirm activation
    prog_dialog.update(83, 'Confirming activation')
    session.headers = {}
    session.headers.update(
        {'Authorization': 'Bearer {0}'.format(access_token)})
    confirm = json.loads(session.get(config.ENTITLEMENTS_URL).text)
    if len(confirm.get('entitlements')) < 1:
        raise AussieAddonsException('Telstra ID activation failed')

    session.close()
    prog_dialog.update(100, 'Finished!')
    prog_dialog.close()
    return json.dumps({'pai': str(userid), 'bearer': access_token})
