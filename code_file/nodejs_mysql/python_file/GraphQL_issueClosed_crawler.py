import requests

REPO_PATH = 'https://api.github.com/graphql'

class graphql_api_crawler_closed(object):
	def __init__(self, repo_name, headers, user_name):
		self.repo_name = repo_name
		self.headers = headers
		self.user_name = user_name
		self.query = '''
		{
			repository (owner: "''' + self.user_name + '''", name: "''' + self.repo_name + '''") {
				issues (last: 1, states: CLOSED) {
					totalCount
				}
			}
		}
		'''

	def run_query(self):
		request = requests.post(REPO_PATH, json={'query': self.query}, headers=self.headers)
		if request.status_code == 200:
				return request.json()
		else:
			raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, self.query))
