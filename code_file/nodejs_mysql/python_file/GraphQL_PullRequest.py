import requests

REPO_PATH = 'https://api.github.com/graphql'

class graphql_api_crawler_pr(object):
	def __init__(self, repo_name, headers, user_name, query_status, cursor = "None"):
		self.repo_name = repo_name
		self.headers = headers
		self.user_name = user_name
		if query_status == 'S':
			self.query = '''
			{
				repository (owner: "''' + self.user_name + '''", name: "''' + self.repo_name + '''") {
	                pullRequests (first: 100) {
	                    totalCount
						edges {
							node {
								number
								state
							}
						}
						pageInfo {
							startCursor
						}
	                }
				}
			}
			'''
		else :
			self.query = '''
			{
				repository (owner: "''' + self.user_name + '''", name: "''' + self.repo_name + '''") {
	                pullRequests (first: 100, after: "''' + cursor + '''") {
	                    totalCount
						edges {
							node {
								number
								state
							}
						}
						pageInfo {
							startCursor
						}
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
