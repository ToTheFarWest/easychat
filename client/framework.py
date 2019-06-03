import requests
from requests.auth import HTTPBasicAuth

class EasyChat():
    url = ''
    token = ''

    def __init__(self, url):
        self.url = url
    
    def login(self, username, password):
        r = requests.get(self.url + 'token', auth = HTTPBasicAuth(username, password))
        if r.status_code == requests.codes.ok:
            self.token = r.json()['token'].encode()
            return True
        return False
    
    def register(self, username, password):
        r = requests.post(self.url + 'users', json={'username': username, 'password': password})
        if r.status_code == requests.codes.ok:
            self.login(username, password)
            return True
        return False
    
    def get_inbox(self):
        r = requests.get(self.url + 'messages', auth = HTTPBasicAuth(self.token, ''))
        if r.status_code == requests.codes.ok:
            return r.json()['messages']
        return False
    
    def get_messages_from_user(self, id):
        r = requests.get(self.url + 'messages/' + str(id), auth = HTTPBasicAuth(self.token, ''))
        if r.status_code == requests.codes.ok:
            return r.json()['messages']
    
    def send_message(self, id, message):
        r = requests.post(self.url + 'messages/' + str(id), auth = HTTPBasicAuth(self.token, ''), json={'message': message})
        if r.status_code == requests.codes.ok:
            return r.json()['message']
        return False

    def get_all_users(self):
        r = requests.get(self.url + 'users', auth = HTTPBasicAuth(self.token, ''))
        if r.status_code == requests.codes.ok:
            return r.json()['users']
        return False
    
    def get_user_id(self, username):
        r = requests.get(self.url + 'users/' + username, auth = HTTPBasicAuth(self.token, ''))
        if r.status_code == requests.codes.ok:
            return r.json()['id']
        return False
    