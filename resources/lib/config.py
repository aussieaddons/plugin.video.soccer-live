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
              'Videos',
              'Settings']

CONFIG_URL = 'https://gateway.ffa.football/mobile/hub/config'

HOME_URL = 'https://gateway.ffa.football/mobile/hub/home?preferences=aleague,socceroos,matildas,wleague,yleague,ffacup,npl'

VIDEOS_URL = 'https://gateway.ffa.football/content/aleague/videos?offset=0&limit=50'

BC_URL = 'https://edge.api.brightcove.com/playback/v1/accounts/{0}/videos/{1}'

BC_POLICYS = {'5519514577001': 'BCpkADawqM0j7AXGHFi_Dwx883WcrB6UvwJHuWlGKbtxY-isLlgM48Ck0TfWgJvo38YKyAebRSKVM2eZ3aLBomKWx63vH4QEcFJqWBSCmidqcI2CJxSNYKkaW3S0KlPhQg2KcNx0oA_1VjAK',
              '5519514578001': 'BCpkADawqM0r9EEGoAc_vGhRKzA9LNT8kbAUfWYmdoVVB1NlYGrCt58_3Ky50L_rVj4gcYjA4WWG7DP1lA4LBDrqik98PdHN9ivVl9mQ8l2jzkf7nQqeTFB-5FKxmuhBDZ5_9GwcNDJFO-V7',
              '5519514571001': 'BCpkADawqM3SGkvPiiweCR4BrANOi6Wu3dtzOIZVrDGY_XcQuOAVEU5_ubheHLKzCmBBBcq3IsAyhWrKss_xIMIJj_hrIEovLg2xNmFDyR00ojao3McEmOMDwk36iK5v-9xVbkbCWabCNRaZ',
              '5519514572001': 'BCpkADawqM3qdGnXQkUk1OiqcwLAl5pM5hbynJDi52VVRMyiWZqc0dPaCu55y1nJmH49BFSJNHj1lveEVvXH_BdX8G0MaP4Tb0wKk0GOuUU-q0P9eQZNZg52R_S7XkS4WhvxYZLbtLMzpQJs',
              '5519514573001': 'BCpkADawqM0a2uwu4YiOyVlm9L9HcSCW8tFT3KhCYS-qD2vgsyy7SWALmQF6CsS8SjrMzsPT2qsrz8W4U5HItDvXvqSngrQftPe04YvJ3lVxvNl8TG5T3qWSzqtQHZxeo1Oo2gPMjXNGsxXt',
              '5519514574001': 'BCpkADawqM03yDM88JKXMgU0sWi9CCFGZI-0W2a2DsKW3dLR8pl60Lp8w5mZ2KFoX4VRaKf2C0EAR2HTODKU-31SQL1sPadUHcCyitDS1nMfTGplN6nCobcx_eaI2y7vP0ZfM0roCwRifhdN',
              '5519514575001': 'BCpkADawqM1qoT9hdCPQapbHacGAuZkTbXHrzsZrcJmLeO1O8iw4NxjWC5nr3IDfhZKX4BLcJxEYni79JlYTf96eC3tx0ldTNYYbL8Sk8EljSt_4j8Zc05YJ7PdHOw907E1pZl0Z2nzHfOcz',
              '5472387882001': 'BCpkADawqM27fXg9qQmpIm67ZxQq_PcLYENoWW-3FiLR1QmXph9PM2HuYw_nkTvnCRU3djpjWHJ81IBsw5fRCYFtuFTAJoch_wxrqr1DsPpieYAv-3sXPakRUfMPbPUbqTYKF5jHSYyENMzX'}

USER_AGENT = 'Dalvik/2.1.0 (Linux; U; Android 6.0.1; m8 Build/MOB31K)'

USER_AGENT_LONG = 'Mozilla/5.0 (Linux; Android 6.0; HTC One_M8 Build/MRA58K.H15; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/56.0.2924.87 Mobile Safari/537.36'

TELSTRA_AUTH_URL = 'https://tapi.telstra.com/v1/media-stream/auth/token?code={code}&pai={pai}&provider=ooyala&partnerId=FFA'

OOYALA_PCODE = 'xoNG0yOk4f4VR8pLKAKNukJ-gdEr'

OOYALA_AUTH_URL = 'http://player.ooyala.com/sas/player_api/v1/authorization/embed_code/{pcode}/{videoid}?device=android_html&domain=http%3A%2F%2Fwww.ooyala.com&embedToken={embedtoken}&supportedFormats=dash%2Cakamai_hd2_vod_hls%2Cmp4%2Cm3u8%2Chls%2Cakamai_hd2_hls'


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
SPC_HEADERS = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'en-AU,en-US;q=0.9',
               'User-Agent': USER_AGENT_LONG,
               'X-Requested-With': 'com.ffa.hal'}

SPC_URL = 'http://hub.telstra.com.au/sp2018-ffa-app?tpUID={0}&offerId=45d09e09-6472-43fa-9f24-d328d9b25ec7&type=SportPassConfirmation&device=mobile&cid=FFA_App'

SSO_PARAMS = {'redirect_uri': 'https://hub.telstra.com.au/offers/content/cached/callback.html',
              'response_type': 'id_token token',
              'scope': 'openid email profile phone telstra.user.sso.profile'}

SSO_URL = 'https://tapi.telstra.com/v1/sso/auth'

SSO_HEADERS = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'en-AU,en-US;q=0.9',
               'Cache-Control': 'max-age=0',
               'Connection': 'keep-alive',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': USER_AGENT_LONG,
               'X-Requested-With': 'com.ffa.hal'}

SIGNON_HEADERS = {'Connection': 'keep-alive', 
                  'Cache-Control': 'max-age=0', 
                  'Origin': 'https://signon.telstra.com', 
                  'Upgrade-Insecure-Requests': '1', 
                  'User-Agent': USER_AGENT_LONG, 
                  'Content-Type': 'application/x-www-form-urlencoded', 
                  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 
                  'Accept-Encoding': 'gzip, deflate', 
                  'Accept-Language': 'en-AU,en-US;q=0.8'}
                        
SIGNON_URL = 'https://signon.telstra.com/login'

SIGNON_DATA = {'goto': 'https://signon.telstra.com/federation/saml2?SPID=telstramedia', 'gotoOnFail': '', 'username': None, 'password': None}
                        
OFFERS_URL = 'https://tapi.telstra.com/v1/media-products/catalogues/media/offers'

HUB_URL = 'http://hub.telstra.com.au/sp2017-netball-app'

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
OFFER_ID = '45d09e09-6472-43fa-9f24-d328d9b25ec7'

MOBILE_ID_URL = 'http://medrx.telstra.com.au/online.php'

MOBILE_CLIENT_ID = 'yGQTEDLGiWeVBogNzKuZAAt6x1yVk3Ot'

MOBILE_CLIENT_SECRET = 'zsbhQBtJ9Towbac7'

MOBILE_TOKEN_PARAMS = {'client_id': MOBILE_CLIENT_ID,
                      'client_secret': MOBILE_CLIENT_SECRET,
                      'grant_type': 'client_credentials',
                      'scope': 'MEDIA-ENTITLEMENTS-API MEDIA-PRODUCTS-API MEDIA-COMMERCE-API MY-OFFERS-BFF',
                      'x-user-idp': 'ngp'}

MOBILE_ORDER_JSON = {"offer": {"id":OFFER_ID}, "serviceType":"MSISDN"}
