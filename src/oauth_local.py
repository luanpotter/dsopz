import http
import os
import urllib
import urlparse
import sys
import datetime
import json
import webbrowser
import util
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

class Error(Exception):
	"""Exceptions"""

def __config():
	return { 
		'client_id': '765762103246-g936peorj64mgveoqhai6ohv4t5qc5qb.apps.googleusercontent.com',
		'client_secret': 'ayQpUnTqvIxgV1XY9e-ItyC8',
		'scopes': [
			'https://www.googleapis.com/auth/cloud-platform',
			'https://www.googleapis.com/auth/datastore',
			'https://www.googleapis.com/auth/userinfo.email'
		]
	}

def get_first_token(port, code):
	config = __config()
	content = http.req_json('POST', 'https://www.googleapis.com/oauth2/v3/token', urllib.urlencode({
		'code': code,
		'client_id': config['client_id'],
		'client_secret': config['client_secret'],
		'redirect_uri': 'http://localhost:%s/redirect_uri' % (port),
		'grant_type': 'authorization_code'
	}), { 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8' })
	now = int(datetime.datetime.now().strftime("%s"))
	expires_in = content['expires_in']
	content['created'] = now
	content['expires'] = now + expires_in
	__write_file(content)
	print 'Done'

class OAuthHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		parsed = urlparse.urlparse(self.path)
		_, port = self.server.socket.getsockname()
		params = urlparse.parse_qs(parsed.query)
		if not params.get('code'):
			print 'Error'
			print json.dumps(params, indent=True)
		else:
			get_first_token(port, params['code'][0])
		self.send_response(302)
		self.send_header('Location', 'http://github.com/murer/dsopz')
		self.send_header('Content-type','text/plain')
		self.end_headers()
		self.wfile.write("Ok")

def __auth_file():
	directory = os.path.expanduser('~')
	if directory == '/':
		directory = '.'
	return directory + '/.dsopz/auth.json'

def __delete_file():
	try:
		os.remove(__auth_file())
	except OSError:
		pass

def __write_file(content):
	c = json.dumps(content, indent=True)
	name = __auth_file()
	util.makedirs(os.path.dirname(name))
	with open(name, 'w') as f:
		f.write(c + '\n')

def __read_file():
	if not os.path.isfile(__auth_file()):
		return None 
	with open(__auth_file(), 'r') as f:
		c = f.read()
	return json.loads(c)

def login():
	__delete_file()
	config = __config()
	server = HTTPServer(('localhost', 0), OAuthHandler)
	_, port = server.socket.getsockname()
	url = 'https://accounts.google.com/o/oauth2/auth?' + urllib.urlencode({
		'client_id': config['client_id'],
		'redirect_uri': 'http://localhost:%s/redirect_uri' % (port),
		'response_type': 'code',
		'scope': ' '.join(config['scopes']),
		'approval_prompt': 'force',
		'access_type': 'offline'
	})
	try:
		webbrowser.open(url, new=1, autoraise=True)
		server.handle_request()
	finally:
		util.close(server.socket)

def __refesh_token(auth):
	config = __config()
	content = http.req_json('POST', 'https://www.googleapis.com/oauth2/v3/token', urllib.urlencode({
		'refresh_token': auth['refresh_token'],
		'client_id': config['client_id'],
		'client_secret': config['client_secret'],
		'grant_type': 'refresh_token'
	}), { 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8' })
	now = int(datetime.datetime.now().strftime("%s"))
	expires_in = content['expires_in']
	content['created'] = now
	content['expires'] = now + expires_in
	content['refresh_token'] = auth['refresh_token']
	__write_file(content)

def get_token():
	auth = __read_file()
	if not auth:
		raise Error('You need to login')
	now = int(datetime.datetime.now().strftime("%s"))
	if now > auth['expires'] - 60:
		__refesh_token(auth)
	auth = __read_file()
	if not auth:
		raise Error('You need to login')
	return auth['access_token']

def __main():
	login()

if __name__ == '__main__':
	__main()