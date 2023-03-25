import time
import urllib.parse as parse
import webbrowser
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from requests.auth import HTTPBasicAuth

OAUTH_AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'
OAUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'

# Change to your application settings
class Settings:
    client_id = 'CLIENT_ID'
    client_secret = 'CLIENT_SECERT'
    redirect_uri = 'REDIRECT_URI'


def authenticate(scope=None):
    '''Implement OAuth 2 Spotify authentication'''
    # Application: Request authorization to access data
    payload = {'client_id': Settings.client_id,
               'response_type': 'code',
               'redirect_uri': Settings.redirect_uri,
               'show_dialog': 'true'} # allow second account to login
    if scope:
        payload['scope'] = scope
    auth_url = '{}?{}'.format(OAUTH_AUTHORIZE_URL, parse.urlencode(payload))
    # Spotify: Displays scopes & prompts user to login (if required)
    # User: Logs in, authorizes access
    webbrowser.open(auth_url)

    response = input('Enter the URL you were redirected to: ')
    code = parse.parse_qs(parse.urlparse(response).query)['code'][0]

    payload = {'redirect_uri': Settings.redirect_uri,
               'code': code,
               'grant_type': 'authorization_code'}
    if scope:
        payload['scope'] = scope

    # Application: Request access and refresh tokens
    # Spotify: Returns access and refresh tokens
    auth = HTTPBasicAuth(Settings.client_id, Settings.client_secret)
    response = requests.post(OAUTH_TOKEN_URL, data=payload, auth=auth)
    if response.status_code != 200:
        response.raise_for_status()
    token_info = response.json()
    token_info['expires_at'] = int(time.time()) + token_info['expires_in']
    token_info['scope'] = scope
    return token_info


def show_tracks(results):
    for item in results['items']:
        track = item['track']
        name = (track['artists'][0]['name'], track['name'])
        with open("file","a", encoding="utf-8") as f:
            f.write(str(name) + "\n")

if __name__ == '__main__':
    user_a = authenticate(scope='user-library-read')
    sp = spotipy.Spotify(auth= user_a['access_token'])
    results = sp.current_user_saved_tracks(limit=1, offset=0)
    while results['next']:
        results = sp.next(results)
        show_tracks(results)

