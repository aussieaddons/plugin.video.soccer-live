# flake8: noqa

NAME = 'Soccer Live'
ADDON_ID = 'plugin.video.soccer-live'

GITHUB_API_URL = 'https://api.github.com/repos/aussieaddons/plugin.video.soccer-live'
ISSUE_API_URL = GITHUB_API_URL + '/issues'
ISSUE_API_AUTH = 'eGJtY2JvdDo1OTQxNTJjMTBhZGFiNGRlN2M0YWZkZDYwZGQ5NDFkNWY4YmIzOGFj'
GIST_API_URL = 'https://api.github.com/gists'

MAX_LIVEQUAL = 4
MAX_REPLAYQUAL = 7

CATEGORIES = ['Live Matches',
              'Match Replays',
              'Videos',
              'Settings']

CONFIG_URL = 'https://gateway.ffa.football/mobile/hub/config'

HOME_URL = 'https://gateway.ffa.football/mobile/hub/home?preferences=aleague,socceroos,matildas,wleague,yleague,ffacup,npl'

MATCHES_URL = 'https://gateway.ffa.football/football/{0}'

VIDEOS_URL = 'https://gateway.ffa.football/content/aleague/videos?offset=0&limit=50'

MATCH_DATA_URL = 'https://gateway.ffa.football/content/{tag}/match/{match}'

BC_URL = 'https://edge.api.brightcove.com/playback/v1/accounts/{0}/videos/{1}'

SIGN_URL = 'https://api.afl.com.au//keyserver/urlSigning?url={0}'

USER_AGENT = 'Dalvik/2.1.0 (Linux; U; Android 6.0.1; m8 Build/MOB31K)'

USER_AGENT_LONG = 'Mozilla/5.0 (Linux; Android 6.0; HTC One_M8 Build/MRA58K.H15; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/56.0.2924.87 Mobile Safari/537.36'

MEDIA_AUTH_URL = 'https://tapi.telstra.com/v1/media-stream/auth/token?code={code}&pai={pai}&provider=signed&partnerId=FFA'

OOYALA_PCODE = 'xoNG0yOk4f4VR8pLKAKNukJ-gdEr'

OOYALA_AUTH_URL = 'http://player.ooyala.com/sas/player_api/v1/authorization/embed_code/{pcode}/{videoid}?device=html5&domain=http%3A%2F%2Fwww.ooyala.com&embedToken={embedtoken}&supportedFormats=dash%2Cakamai_hd2_vod_hls%2Cmp4%2Cm3u8%2Chls%2Cakamai_hd2_hls'


OAUTH_HEADERS = {'User-Agent': 'okhttp/3.10.0',
                 'Accept-Encoding': 'gzip'}

OAUTH_DATA = {'client_id': 'yGQTEDLGiWeVBogNzKuZAAt6x1yVk3Ot',
              'client_secret': 'zsbhQBtJ9Towbac7',
              'grant_type': 'client_credentials',
              'scope': 'MEDIA-ENTITLEMENTS-API MEDIA-PURCHASE-API',
              'x-user-idp': 'PARTNER'}

OAUTH_URL = 'https://tapi.telstra.com/v1/media-entitlements/oauth/token'

ENTITLEMENTS_URL = 'https://tapi.telstra.com/v1/media-entitlements/entitlements?tenantid=ffa'

#Paid auth
MEDIA_PURCHASE_URL = 'https://tapi.telstra.com/v1/media-purchase/users/{0}/subscriptions/?partnerId=FFA'

AWS_CLIENT_ID = '4rtrirgracuqrpn4fgaia0skc0'

AWS_POOL_ID = 'ap-southeast-2_3RiyW2G3K'

AWS_REGION = 'ap-southeast-2'

#Free Auth
MYID_AUTHORIZATION_URL = 'https://myid.telstra.com/identity/as/authorization.oauth2'

MYID_TOKEN_URL = 'https://myid.telstra.com/identity/as/token.oauth2'

MYID_TOKEN_PARAMS = {
    'redirect_uri': 'https://hub.telstra.com.au/offers/content/cached'
                    '/callback.html',
    'grant_type': 'authorization_code'
}

MYID_RESUME_AUTHORIZATION_URL = 'https://myid.telstra.com/identity/as/{0}/resume/as/authorization.ping'

MYID_AUTH_RESUME_DATA = {
    'pf.rememberUsername': 'on',
    'pf.ok': 'clicked',
    'pf.cancel': '',
    'pf.adapterId': 'upAdapter'
}

SSO_SESSION_HANDLER_URLS = [
    'https://signon.telstra.com/SSOSessionHandler',
    'https://signon.bigpond.com/SSOSessionHandler',
    'https://signon.telstra.com.au/SSOSessionHandler'
]

MYID_AUTH_PARAMS = {
    'redirect_uri': 'https://hub.telstra.com.au/offers/content/cached'
                    '/callback.html',
    'response_type': 'code',
    'scope': 'openid app.oneplace',
    'code_challenge_method': 'S256',
    'response_mode': 'query'}

MYID_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
              'image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, '
                       'deflate',
    'Accept-Language': 'en-AU,en-US;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'X-Requested-With': 'com.telstra.nrl'}

SPC_HEADERS = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'en-AU,en-US;q=0.9',
               'User-Agent': USER_AGENT_LONG,
               'X-Requested-With': 'com.ffa.hal'}

SPC_URL = 'http://hub.telstra.com.au/sp2018-ffa-app?tpUID={0}&offerId=45d09e09-6472-43fa-9f24-d328d9b25ec7&type=SportPassConfirmation&device=mobile&cid=FFA_App'


                        
OFFERS_URL = 'https://tapi.telstra.com/v1/media-products/catalogues/media/offers'

HUB_URL = 'http://hub.telstra.com.au/sp2018-ffa-app'

MEDIA_ORDER_HEADERS = {'Content-Type': 'application/json', 
                       'Accept': 'application/json, text/plain, */*', 
                       'Connection': 'keep-alive', 
                       'Origin': 'https://hub.telstra.com.au',
                       'User-Agent': USER_AGENT_LONG, 
                       'Accept-Encoding': 'gzip, deflate', 
                       'Accept-Language': 'en-AU,en-US;q=0.8', 
                       'X-Requested-With': 'com.ffa.hal'}

MEDIA_ORDER_URL = 'https://tapi.telstra.com/v1/media-commerce/orders'

MEDIA_ORDER_JSON = '{{"serviceId":"{0}","serviceType":"MSISDN","offer":{{"id":"{1}"}},"pai":"{2}"}}'


#Mobile Auth
MOBILE_OAUTH_URL = 'https://tapi.telstra.com/v1/media-commerce/oauth/token'

MOBILE_ID_URL = 'http://medrx.telstra.com.au/online.php'

OFFER_ID = '45d09e09-6472-43fa-9f24-d328d9b25ec7'

MOBILE_CLIENT_ID = 'yGQTEDLGiWeVBogNzKuZAAt6x1yVk3Ot'

MOBILE_CLIENT_SECRET = 'zsbhQBtJ9Towbac7'

MOBILE_TOKEN_PARAMS = {'client_id': MOBILE_CLIENT_ID,
                      'client_secret': MOBILE_CLIENT_SECRET,
                      'grant_type': 'client_credentials',
                      'scope': 'MEDIA-ENTITLEMENTS-API MEDIA-PURCHASE-API',
                      'x-user-idp': 'NGP'}

MOBILE_ORDER_JSON = {"offer": {"id":OFFER_ID}, "serviceType":"MSISDN"}
