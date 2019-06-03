import threading
from datetime import datetime

from repo_commit import repo_diff_info
from GraphQL_crawler import graphql_api_crawler
from GraphQL_commit_crawler import graphql_api_crawler_commit
from GraphQL_issueOpen_crawler import graphql_api_crawler_open
from GraphQL_issueClosed_crawler import graphql_api_crawler_closed
from User_GraphQL_crawler import user_graphql_api_crawler


class get_info(object):
	def __init__(self, header, user_name):
		self.header = header
		self.user_name = user_name
		self.repoLangs = dict()
		self.repoTopics = dict()
		self.userEvents = dict()
		self.repoCommit_info = dict()
		self.repoBranches = dict()
		self.repoIssue = dict()
		self.repoComment = dict()
		self.repoCollaborator = dict()

	# def user_info_crawling(self, q):
	def user_info_crawling(self):
		Uinfo_crawler = user_graphql_api_crawler(self.header, self.user_name)
		Uinfo_data = Uinfo_crawler.run_query()

		avatarUrl = Uinfo_data['data']['user']['avatarUrl']
		bio = Uinfo_data['data']['user']['bio']
		location = Uinfo_data['data']['user']['location']
		github_url = Uinfo_data['data']['user']['url']
		websiteUrl = Uinfo_data['data']['user']['websiteUrl']
		company = Uinfo_data['data']['user']['company']

		# q.put([avatarUrl, bio, location, name, github_url, websiteUrl])
		return [avatarUrl, bio, location, github_url, websiteUrl, company]
	
	def commits_crawler(self, commits_json, committed_data, repo):
		commits_data = commits_json['data']['repository']['defaultBranchRef']['target']['history']['edges']
		until_date = commits_data[len(commits_data)-1]['node']['committedDate'] #commits_data의 경우 정해진 개수가 표시되기에 date를 저장하여 지속적으로 탐색
		while len(commits_data) != 1:
			for data in commits_data:
				if data['node']['author']['name'] == self.user_name:
					committed_data[data['node']['committedDate'][:10]] = [data['node']['additions'], data['node']['deletions']]
			next_commit_crawler = graphql_api_crawler_commit(repo, self.header, self.user_name, until_date)
			commits_data = next_commit_crawler.run_query()
		self.repoCommit_info[repo] = committed_data
	
	# def repo_info_crawling(self, q):
	def repo_info_crawling(self):
		repo_info = repo_diff_info(self.header, self.user_name)
		repo_names = repo_info.get_repo_info()
		
		t3 = threading.Thread(target=repo_info.get_event, args=(self.userEvents,))
		t3.start()
		t3.join()
			
		now_date = datetime.now()
		now_date = (now_date.isoformat()[:19] + 'Z')

		repo_names_dict = dict()
		total_repo_info = list()
		commit_ranking = dict()

		committed_data = dict() # { committedDate : [additions, deletions] }
		#topic을 가져오기 위한 새로운 생성자
		for i, repo in enumerate(repo_names):
			repo_crawler = graphql_api_crawler(repo, self.header, self.user_name)
			repo_data = repo_crawler.run_query()
			
			commit_crawler = graphql_api_crawler_commit(repo, self.header, self.user_name, now_date)
			commit_data = commit_crawler.run_query()

			issue_open_crawler = graphql_api_crawler_open(repo, self.header, self.user_name)
			issue_open = issue_open_crawler.run_query()
			issue_open_totalCount = issue_open['data']['repository']['issues']['totalCount']

			issue_closed_crawler = graphql_api_crawler_closed(repo, self.header, self.user_name)
			issue_closed = issue_closed_crawler.run_query()
			issue_closed_totalCount = issue_closed['data']['repository']['issues']['totalCount']
			
			#open & cloase get count list
			open_close_issue_count = list()
			#collaborator list
			collaborator_list = list()
			#user가 가지고 있는 repository의 language들의 list를 가져온다.
			t1 = threading.Thread(target=repo_info.get_repo_lang, args=(repo, self.repoLangs,))
			t2 = threading.Thread(target=repo_info.get_repo_topic, args=(repo, self.repoTopics,))
			t5 = threading.Thread(target=repo_info.get_branches, args=(repo, self.repoBranches,))
			t6 = threading.Thread(target=repo_info.get_issues, args=(repo, open_close_issue_count,))
			t7 = threading.Thread(target=self.commits_crawler, args=(commit_data, committed_data, repo,))
			t8 = threading.Thread(target=repo_info.get_issues_comment, args=(repo, self.repoComment,))
			t9 = threading.Thread(target=repo_info.get_collaborators, args=(repo, collaborator_list,))
			#------------------------------------------------------------------
			t1.start(); t2.start(); t5.start(); t6.start(); t7.start(); t8.start(); t9.start()

			t1.join(); t2.join(); t5.join(); t6.join(); t7.join(); t8.join()
			
			#Choose the case with the highest number of commit attempts.
			if repo_data['data']['repository']['defaultBranchRef'] == None:
				continue
			
			total_repo_info.append([i, repo_data['data']['repository']['url'], repo_data['data']['repository']['stargazers']['totalCount'], repo_data['data']['repository']['watchers']['totalCount'], repo_data['data']['repository']['forkCount'], repo_data['data']['repository']['createdAt'][:10]])
			commit_ranking[i] = repo_data['data']['repository']['defaultBranchRef']['target']['history']['totalCount']
			
			repo_names_dict[i] = repo
			#etc_info[repo] = total_count
			#etc_info -> {repo_name : [total_count, url]}
			open_close_issue_count.append(issue_open_totalCount)
			open_close_issue_count.append(issue_closed_totalCount)
			self.repoIssue[repo] = open_close_issue_count

			self.repoCollaborator[repo] = collaborator_list

		#print(self.repoCommit_info)
		#print(self.repoBranches)
		#print(self.repoIssue)
		#print(self.repoComment)
		print(self.repoCollaborator)

		#commit순으로 정리하여 가장 큰 4개를 끊는다.
		commit_ranks_key = sorted(commit_ranking.items(), key=lambda x: x[1], reverse=True)
		commit_ranks_key = commit_ranks_key[:4]
		# q.put(etc_info)
		return repo_names_dict, total_repo_info, commit_ranks_key, self.repoLangs, self.repoTopics, self.userEvents, self.repoBranches, self.repoIssue, self.repoComment
