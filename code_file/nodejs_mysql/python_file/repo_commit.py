import json
import urllib
import urllib.request
from datetime import datetime

REPO_PATH = 'https://api.github.com/users/{id}/repos'
LANG_PATH = 'https://api.github.com/repos/{id}/{repo}/languages'
TOPIC_PATH = 'https://api.github.com/repos/{id}/{repo}/topics'
EVENT_PATH = 'https://api.github.com/users/{id}/events'
COMMIT_ACTIVITY_PATH = 'https://api.github.com/repos/{id}/{repo}/stats/commit_activity'
BRANCH_PATH = 'https://api.github.com/repos/{id}/{repo}/branches'
ISSUE_PATH = 'https://api.github.com/repos/{id}/{repo}/issues'
ISSUE_COMMENT_PATH = 'https://api.github.com/repos/{id}/{repo}/issues/comments'
COLLABORATE_PATH = 'https://api.github.com/repos/{id}/{repo}/collaborators'


class repo_diff_info(object):
	def __init__(self, header, name):
		self.headers = header
		self.name = name
		self.repoNames = list()

	def load_data(self, opener):
		ur = urllib.request.urlopen(opener)
		raw_data = ur.read()
		encoding = ur.info().get_content_charset('utf-8') #Set encoding
		data = json.loads(raw_data.decode(encoding))
		return data

	def get_repo_info(self):
		headers = self.headers
		request_dict = {'id': self.name}
		response = urllib.request.Request(REPO_PATH.format_map(request_dict), headers = headers)
		response_json = self.load_data(response)
		repos_license = dict()
		for data in response_json:
			self.repoNames.append(data['name'])
			if data['license'] != None:
				repos_license[data['name']] = data['license']['name']
		return self.repoNames, repos_license

	def get_repo_lang(self, repo, lang_dict):
		headers = self.headers
		request_dict = {'id': self.name, 'repo': repo}
		response_lang = urllib.request.Request(LANG_PATH.format_map(request_dict), headers = headers)
		response_lang_json = self.load_data(response_lang)

		for repo in response_lang_json.keys():
			if repo in lang_dict.keys():
				lang_dict[repo] += 1
			else:
				lang_dict[repo] = 1

	def get_repo_topic(self, repo, topic_dict):
		headers = self.headers
		request_dict = {'id': self.name, 'repo': repo}
		response_topic = urllib.request.Request(TOPIC_PATH.format_map(request_dict), headers = headers)
		response_topic_json = self.load_data(response_topic)

		for topic in response_topic_json['names']:
			if topic in topic_dict.keys():
				topic_dict[topic] += 1
			else:
				topic_dict[topic] = 1

	def get_event(self, event_dict):
		headers = self.headers
		request_dict = {'id': self.name}
		response_event = urllib.request.Request(EVENT_PATH.format_map(request_dict), headers = headers)
		response_event_json = self.load_data(response_event)

		for event in response_event_json:
			e = event['type']
			if e in event_dict:
				event_dict[e] += 1
			else:
				event_dict[e] = 1

	def get_branches(self, repo, branch_dict):
		headers = self.headers
		request_dict = {'id': self.name, 'repo': repo}
		response_branch = urllib.request.Request(BRANCH_PATH.format_map(request_dict), headers = headers)
		response_branch_json = self.load_data(response_branch)

		branch_list = list()
		for branch in response_branch_json:
			branch_list.append(branch['name'])
		if len(branch_list) > 1:
			branch_dict[repo] = True
		else:
			branch_dict[repo] = False

	def get_issues(self, repo, issue_count):
		headers = self.headers
		request_dict = {'id': self.name, 'repo': repo}
		response_issue = urllib.request.Request(ISSUE_PATH.format_map(request_dict), headers = headers)
		response_issue_json = self.load_data(response_issue)
		issue_open_count = 0
		issue_close_count = 0
		for issue in response_issue_json:
			if self.name == issue['user']['login'] and issue['state'].lower() == 'open':
				issue_open_count += 1
			else:
				issue_close_count += 1
		issue_count.append(issue_open_count)
		issue_count.append(issue_close_count)

	def get_issues_comment(self, repo, issue_comment):
		headers = self.headers
		request_dict = {'id': self.name, 'repo': repo}
		response_comment = urllib.request.Request(ISSUE_COMMENT_PATH.format_map(request_dict), headers = headers)
		response_comment_json = self.load_data(response_comment)

		comment_count = 0
		for comment in response_comment_json:
			if self.name != comment['user']['login']: # 자신이 올린 issue에 대한 comment는 제외한다.
				comment_count += 1

		issue_comment[repo] = comment_count

	def get_collaborators(self, repo, collaborate_list):
		headers = self.headers
		request_dict = {'id': self.name, 'repo': repo}
		response_collaborate = urllib.request.Request(COLLABORATE_PATH.format_map(request_dict), headers = headers)
		response_collaborate_json = self.load_data(response_collaborate)
		for user in response_collaborate_json:
			if user['login'] != self.name:
				collaborate_list.append(user['login'])
