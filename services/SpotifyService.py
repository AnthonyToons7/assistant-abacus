import os
import sys
import json
import requests
import base64
import webbrowser
import threading
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QMessageBox
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from dotenv import load_dotenv

from core.storage import get_saved_settings
load_dotenv()

class SpotifyService:
    def __init__(self, parent=None):
        self.client_id = os.environ.get("SPOTIFY_API_KEY")
        self.client_secret = os.environ.get("SPOTIFY_API_SECRET")
        self.redirect_uri = "https://example.com/callback"
        self.scopes = "user-modify-playback-state user-read-playback-state playlist-read-private playlist-read-collaborative"
        self.access_token = None
        self.refresh_token = None
        self.base_url = "https://api.spotify.com/v1"
        self.parent = parent
        self.login_popup_open = False
        self.pending_action = {
            "prompt_type": None,
            "prompt_qry": None,
            "prompt_owner": None,
            "prompt_extra": "my desktop",
            "command": None,
        }

    def set_pending_action(self, prompt_type=None, prompt_qry=None, prompt_owner=None, prompt_extra='my desktop', command=None):
        self.pending_action = {
            "prompt_type": prompt_type,
            "prompt_qry": prompt_qry,
            "prompt_owner": prompt_owner,
            "prompt_extra": prompt_extra,
            "command": command,
        }

    def load_token(self):
        if os.path.exists("spotify_token.json"):
            with open("spotify_token.json", "r") as f:
                data = json.load(f)
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")

                if not self.access_token or not self.refresh_token:
                    return False

                if(self.access_token is None or self.refresh_token is None or data == {}):
                    return False
            return True
        print("Spotify token not found.")
        return False

    def connect(self, device_name=None):
        if self.access_token:
            return True
        self.request_login()
        return False

    def save_token(self):
        with open("spotify_token.json", "w") as f:
            json.dump({
                "access_token": self.access_token,
                "refresh_token": self.refresh_token
            }, f)

    def request_login(self):
        if self.login_popup_open:
            return False
        self.login_popup_open = True
        bridge.show_login.emit(self)
        return False

    def _parse_response(self, response):
        try:
            payload = response.json() if response.content else {}
        except ValueError:
            return response.text or {}

        if isinstance(payload, dict):
            error = payload.get("error")
            error_status = error.get("status") if isinstance(error, dict) else None
            if response.status_code == 401 or error_status == 401:
                self.access_token = None
                self.request_login()

        return payload

    def user_login_popup(self, prompt_type='', prompt_qry='', prompt_owner='', prompt_extra=None, command=None):
        pending_action = self.pending_action.copy()
        if prompt_type or prompt_qry or prompt_owner or prompt_extra is not None or command:
            pending_action.update({
                "prompt_type": prompt_type,
                "prompt_qry": prompt_qry,
                "prompt_owner": prompt_owner,
                "prompt_extra": prompt_extra,
                "command": command,
            })

        class LoginPopup(QWidget):
            def __init__(self, service):
                super().__init__()
                self.service = service
                self.pending_action = pending_action.copy()
                self.setWindowTitle("Connect Spotify")
                self.setFixedSize(400, 200)

                layout = QVBoxLayout()

                layout.addWidget(QLabel("Connect Spotify with A.B.A.C.U.S?"))

                self.open_btn = QPushButton("Open Spotify Login")
                layout.addWidget(self.open_btn)

                layout.addWidget(QLabel("Paste the 'code' from the redirect URL here:"))
                self.code_input = QLineEdit()
                layout.addWidget(self.code_input)

                self.submit_btn = QPushButton("Submit Code")
                layout.addWidget(self.submit_btn)

                self.setLayout(layout)

                self.open_btn.clicked.connect(self.open_spotify_login)
                self.submit_btn.clicked.connect(self.submit_code)

            def closeEvent(self, event):
                self.service.login_popup_open = False
                if self in _active_popups:
                    _active_popups.remove(self)
                super().closeEvent(event)

            def open_spotify_login(self):
                auth_url = (
                    "https://accounts.spotify.com/authorize"
                    f"?client_id={self.service.client_id}"
                    "&response_type=code"
                    f"&redirect_uri={self.service.redirect_uri}"
                    f"&scope={self.service.scopes}"
                )
                webbrowser.open(auth_url)

            def submit_code(self):
                code = self.code_input.text().strip()
                if not code:
                    QMessageBox.warning(self, "Error", "Please paste the code from the redirect URL.")
                    return
                self.exchange_code_for_token(code)
                QMessageBox.information(self, "Success", "Spotify login successful!")
                self.hide()
                
                threading.Thread(
                    target=_execute,
                    args=(
                        self.service,
                        self.pending_action["prompt_type"],
                        self.pending_action["prompt_qry"],
                        self.pending_action["prompt_owner"],
                        self.pending_action["prompt_extra"],
                        self.pending_action["command"],
                    ),
                    daemon=True
                ).start()

            def exchange_code_for_token(self, code):
                b64_auth = base64.b64encode(f"{self.service.client_id}:{self.service.client_secret}".encode()).decode()
                r = requests.post(
                    "https://accounts.spotify.com/api/token",
                    headers={"Authorization": f"Basic {b64_auth}"},
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": self.service.redirect_uri
                    }
                )
                resp = r.json()
                self.service.access_token = resp["access_token"]
                self.service.refresh_token = resp.get("refresh_token")
                self.service.save_token()

        popup = LoginPopup(self)
        popup.show()
        return popup

    def get_spotify_device_id(self, device_name=None):
        device_id = None
        devices_resp = self.get("me/player/devices")

        print(devices_resp)

        if not isinstance(devices_resp, dict):
            return False

        devices = devices_resp.get("devices", [])

        if not devices:
            print("No Spotify devices found. Please start Spotify on a device first.")
            return False

        if device_name is not None:
            for d in devices:
                print(d["name"].lower(), device_name.lower())
                if device_name and d["name"].lower() == device_name.lower():
                    device_id = d["id"]
                    print(f"Using device: {d['name']} ({device_id})")
                    break
        
        if device_id is None:
            device_id = devices[0]["id"]
        
        return device_id

    def search_user_playlist(self, name):
        playlists = []
        url = "me/playlists"
        while url:
            resp = self.get(url, params={"limit": 50})
            items = resp.get("items", [])
            playlists.extend(items)
            url = resp.get("next")

        for p in playlists:
            if p["name"].lower() == name.lower():
                return {"type": "playlist", "uri": p["uri"]}
        return None

    def search(self, type, query):
        if type not in ["playlist", "track"]:
            return None

        resp = self.get("search", params={
            "q": query,
            "type": type,
            "limit": 10
        })

        items = resp.get(f"{type}s", {}).get("items", [])
        items = [i for i in items if i]

        if not items:
            return None

        first = items[0]
        return {"type": type, "uri": first["uri"]}

    def play(self, element, device_name=None):
        device_id = self.get_spotify_device_id(device_name)

        if not device_id:
            print("No valid Spotify device found to play on.")
            return False

        if element['type'] == 'song' or element['type'] == 'track':
            r = self.put("me/player/play", data={"device_id": device_id, "uris": [element['uri']]})
        elif element['type'] == 'playlist':
            r = self.put("me/player/play", data={"device_id": device_id, "context_uri": element['uri']})
        
        print("Play response:", r)
        return True

    def pause(self):
        self.put('me/player/pause')

    def resume(self):
        device_id = self.get_spotify_device_id()
        if not device_id:
            return False
        r = self.put("me/player/play", data={"device_id": device_id})
        if r and isinstance(r, dict) and r.get("error"):
            print(f"Error resuming playback: {r['error']}")
            return False
        return True

    def skip(self):
        device_id = self.get_spotify_device_id()
        if not device_id:
            return False
        self.post('me/player/next', data={"device_id": device_id})

    def previous(self):
        device_id = self.get_spotify_device_id()
        if not device_id:
            return False
        self.post('me/player/previous', data={"device_id": device_id})

    def get(self, endpoint, params=None):
        r = requests.get(f"{self.base_url}/{endpoint}", headers={
            "Authorization": f"Bearer {self.access_token}"
        }, params=params)
        return self._parse_response(r)

    def post(self, endpoint, data=None):
        r = requests.post(f"{self.base_url}/{endpoint}", headers={
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }, data=json.dumps(data) if data else None)
        return self._parse_response(r)

    def put(self, endpoint, data=None):
        r = requests.put(f"{self.base_url}/{endpoint}", headers={
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }, data=json.dumps(data) if data else None)
        return self._parse_response(r)

    def delete(self, endpoint, data=None):
        r = requests.delete(f"{self.base_url}/{endpoint}", headers={
            "Authorization": f"Bearer {self.access_token}"
        })
        try:
            return r.json()
        except ValueError:
            return r.text or {}

_active_popups = [] 

class _SpotifyBridge(QObject):
    show_login = pyqtSignal(object)

    def __init__(self):
        super().__init__()

bridge = _SpotifyBridge()

def run(prompt_type, prompt_qry, prompt_owner, prompt_extra='my desktop', command=None):
    spotify = SpotifyService()
    spotify.set_pending_action(prompt_type, prompt_qry, prompt_owner, prompt_extra, command)
    if not spotify.load_token():
        spotify.request_login()
        return
    _execute(spotify, prompt_type, prompt_qry, prompt_owner, prompt_extra, command)

def _show_login_popup(spotify):
    popup = spotify.user_login_popup()
    _active_popups.append(popup)

def _execute(spotify, prompt_type, prompt_qry, prompt_owner, prompt_extra, command=None):
    spotify.set_pending_action(prompt_type, prompt_qry, prompt_owner, prompt_extra, command)

    if not spotify.connect(prompt_extra):
        return

    if prompt_type == 'song':
        element_to_play = spotify.search('track', prompt_qry)
    elif prompt_type == 'playlist':
        element_to_play = (
            spotify.search_user_playlist(prompt_qry) if prompt_owner == 'my' else spotify.search('playlist', prompt_qry)
        )
    else:
        element_to_play = None

    device_name = None
    # if prompt_extra == 'my desktop':
    #     device_name = 'ANTHONY'
    # elif prompt_extra == 'my phone':
    #     device_name = 'A34 van AnthonyToons'
    # elif prompt_extra == 'the office':
    #     device_name = 'Badkamer'

    # device_name = 'ANTHONY'

    saved = get_saved_settings()
    spotify_settings = saved.get("default_spotify_device")

    if(prompt_extra is not None):
        device_name = spotify_settings.get(prompt_extra)
    else: 
        device_name = spotify_settings.get("laptop")

    if element_to_play:
        spotify.play(element_to_play, device_name)
    elif command:
        match command:
            case 'pause':
                spotify.pause()
            case 'resume':
                spotify.resume()
            case 'skip':
                spotify.skip()
            case 'previous':
                spotify.previous()
    else:
        print("No song/playlist found with that name.")


bridge.show_login.connect(_show_login_popup)