# import libraries
from settings import google_drive_credentials
from oauth2client.client import OAuth2WebServerFlow, GoogleCredentials
import httplib2
from googleapiclient.discovery import build

google_drive_info = {
    'scope': 'https://www.googleapis.com/auth/drive',
    'url': 'https://accounts.google.com/o/oauth2/token',
    'version':'v3',
    'name':'drive'
}

class Connect():

    def __init__(self):    
        
        self.scope = google_drive_info['scope']
        self.client_id = google_drive_credentials['client_id']
        self.client_secret = google_drive_credentials['client_secret']
        self.redirect_uri = google_drive_credentials['redirect_uri']
        self.access_code = google_drive_credentials['access_code']
        self.access_token = google_drive_credentials['access_token']
        self.refresh_token = google_drive_credentials['refresh_token']

    def get_service(self):
        if self.access_code == '' or self.access_token == '' or self.refresh_token == '':
            self._start_connection()
        else:
            credentials = GoogleCredentials(
                self.access_token, 
                self.client_id, 
                self.client_secret, 
                self.refresh_token, 
                3920, 
                google_drive_info['url'], 
                'test'
            )
            http = httplib2.Http()
            http = credentials.authorize(http)
            service = build(
                google_drive_info['name'],
                google_drive_info['version'], 
                http=http
            )
            return service

    def _start_connection(self):
        # create connection based on project credentials
        flow = OAuth2WebServerFlow(
            client_id=self.client_id,
            client_secret=self.client_secret,
            scope=self.scope,
            redirect_uri=self.redirect_uri
        )

        # capture different states of connection
        if self.access_code == '':
            # first run prints oauth URL
            auth_uri = flow.step1_get_authorize_url()
            print('----------')
            print('Go to this url and give permissions to google: {0}'.format(auth_uri))
            print('----------')
            print('*Note: Connection not yet established')
        elif self.access_token == '' and self.refresh_token == '':
            # second run returns access and refresh token
            credentials = flow.step2_exchange(self.access_code)
            print('----------')
            print('Access Token: ')
            print(credentials.access_token)
            print('Refresh Token: ')
            print(credentials.refresh_token)
            print('----------')
            print('*Note: Connection not yet established')
        