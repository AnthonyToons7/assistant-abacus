import os
import json
import requests

class SpotifyService():
    def __init__(self):
        self.api_key = os.environ.get('SPOTIFY_API_KEY')
        self.api_secret = os.environ.get('SPOTIFY_API_SECRET')
        self.base_url = 'https://api.spotify.com/v1'
        self.access_token = None

    def connect(self):        
        r = requests.post('https://accounts.spotify.com/api/token', data={
            'grant_type': 'client_credentials',
            'client_id': self.api_key,
            'client_secret': self.api_secret
        })
        self.access_token = r.json().get('access_token')

    def search_song(self, query, track=False, artist=False, album=False):
        self.get('/search', {
            'q': query,
            'type': track,
            'artist': artist,
            'album': album,
        })
    
    def play(self, element):
        if element['type'] == 'song':
            print('playing song')
        elif element['type'] == 'playlist':
            print ('playing playlist')

    def pause(self):
        self.put('me/player/pause')
    
    def resume(self):
        self.put('me/player/play')
    
    def skip(self):
        self.put('me/player/next')
    
    def previous(self):
        self.put('me/player/previous')

    
    def get(self, endpoint, params):
        r = requests.get(f'{self.base_url}/{endpoint}', headers={
            'Authorization': f'Bearer {self.access_token}'
        }, params=params)
        return r.json()

    def post(self, endpoint, data):
        r = requests.post(f'{self.base_url}/{endpoint}', headers={
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
        }, data=json.dumps(data))
        return r.json()

    def put(self, endpoint, data=None):
        r = requests.put(f'{self.base_url}/{endpoint}', headers={
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }, data=json.dumps(data))
        return r.json()

    def delete(self, endpoint, data):
        r = requests.delete(f'{self.base_url}/{endpoint}/{data}', headers={
            'Authorization': f'Bearer {self.access_token}'
        })
        return r.json()