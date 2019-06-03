import base64
import json
import urllib
import urllib.request


class git_certification(object):
	def __init__(self, Uinfo):
		self.user_info = Uinfo

	def get_info2base64(self):
		cert = self.user_info
		cert = cert.encode('utf-8')
		cert = base64.b64encode(cert)
		cert = cert.decode('utf-8')
		return cert
