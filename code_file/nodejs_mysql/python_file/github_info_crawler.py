import threading
from datetime import datetime
import math

from repo_commit import repo_diff_info
from GraphQL_crawler import graphql_api_crawler
from GraphQL_commit_crawler import graphql_api_crawler_commit
from GraphQL_issueOpen_crawler import graphql_api_crawler_open
from GraphQL_issueClosed_crawler import graphql_api_crawler_closed
from User_GraphQL_crawler import user_graphql_api_crawler
from GraphQL_PullRequest import graphql_api_crawler_pr
from GraphQL_PullRequest_Number import graphql_api_crawler_pr_number


class get_info(object):
	def __init__(self, header, user_name):
		self.header = header
		self.user_name = user_name
		self.repoCommit_info = dict()

	# user의 기본 정보들을 수집하는 crawler
	def user_info_crawling(self):
		Uinfo_crawler = user_graphql_api_crawler(self.header, self.user_name)
		Uinfo_data = Uinfo_crawler.run_query()

		avatarUrl = Uinfo_data['data']['user']['avatarUrl']
		bio = Uinfo_data['data']['user']['bio']
		location = Uinfo_data['data']['user']['location']
		github_url = Uinfo_data['data']['user']['url']
		websiteUrl = Uinfo_data['data']['user']['websiteUrl']
		company = Uinfo_data['data']['user']['company']

		return [avatarUrl, bio, location, github_url, websiteUrl, company]

	# 1. repository의 전체 code의 line_count를 구한다. 2. 검색하고자 하는 user가 직접 추가, 제거한 code의 line_count를 구한다.
	def commits_crawler(self, commits_json, committed_data, repo, order, code_line):
		commits_data = commits_json['data']['repository']['defaultBranchRef']['target']['history']['edges']
		until_date = commits_data[len(commits_data)-1]['node']['committedDate'] #commits_data의 경우 정해진 개수가 표시되기에 date를 저장하여 지속적으로 탐색
		addition_code = 0; deletion_code = 0
		while len(commits_data) != 1:
			# repository의 total_code_line_count를 구한다.
			for data in commits_data:
				addition_code += data['node']['additions']
				deletion_code += data['node']['deletions']
				# repository에서 검색하고자 하는 user의 code_line_count를 구한다.
				if data['node']['author']['name'] == self.user_name:
					committed_data[data['node']['committedDate'][:10]] = [data['node']['additions'], data['node']['deletions']]
			# Github API인 v4에서 한 번에 검색하고자 하는 개수는 100개가 한정이기에 이후 데이터는 날짜를 이동해가면서 구한다.
			next_commit_crawler = graphql_api_crawler_commit(repo, self.header, self.user_name, until_date)
			commits_data = next_commit_crawler.run_query()
		self.repoCommit_info[order] = committed_data
		code_line[repo] = int(addition_code) - int(deletion_code)  # repository에 추가한 코드의 줄 수와 삭제한 코드의 줄 수를 addition - deletion 의 형태로 저장

	# pull_request와 관련된 number을 OPEN, CLOSED, MERGED로 구분하여 dict의 형태로 형성
	def pullrequest_crawler(self, pr_json, repo, user_name, headers):
		status = 'S'
		pr_crawler = graphql_api_crawler_pr(repo, headers, user_name, status)
		pr_status_data = pr_crawler.run_query()

		for pr in pr_status_data['data']['repository']['pullRequests']['edges']:
			if pr['node']['state'] not in pr_json:
				pr_json[pr['node']['state']] = repo + '/' + str(pr['node']['number']) # { status: "repo/number,repo/number,..." }
			else:
				pr_json[pr['node']['state']] += "," + repo + '/' + str(pr['node']['number'])

		total_count = pr_status_data['data']['repository']['pullRequests']['totalCount']
		if total_count > 100:
			status = 'C'
			repeat_count = math.ceil(float(total_count - 100) / 100) # 100개 이후 추가적인 개수를 가져올 경우 그 횟수를 계산
			for i in range(repeat_count):
				pr_crawler = graphql_api_crawler_pr(repo, headers, user_name, status, pr_status_data['data']['repository']['pullRequests']['pageInfo']['startCursor'])
				pr_status_data = pr_crawler.run_query()

				for a, pr in enumerate(pr_status_data['data']['repository']['pullRequests']['edges']):
					if a == 0: # cursor의 경우 맨 마지막의 case가 다시 반복되기 때문에 가장 처음을 제외
						continue
					if pr['node']['state'] not in pr_json:
						pr_json[pr['node']['state']] = repo + '/' + str(pr['node']['number']) # { status: "repo/number,repo/number, ..." }
					else:
						pr_json[pr['node']['state']] += "," + repo + '/' + str(pr['node']['number'])

	repo_names = list()
	repo_licenses = dict() #Repository들의 license 정보들이 담겨있다.
	def repo_info_crawling(self):
		repo_info = repo_diff_info(self.header, self.user_name)
		repo_names, repo_licenses = repo_info.get_repo_info()

		now_date = (datetime.now()).isoformat()[:19] + 'Z'

		repo_names_dict = dict() # { 0 : repo1, 1: repo2, ... }
		total_repo_info = list() # repository의 정보가 담긴 리스트
		commit_ranking = dict() # repository별 total commit count
		committed_data = dict() # { repo_committedDate : [additions, deletions] }
		pr_repo_score = dict() # { repo_name : score }
		# repository에 관한 정보를 담는 dictionary
		repo_code_line = dict(); repoLangs = dict(); repoTopics = dict(); userEvents = dict()
		repoBranches = dict(); repoIssue = dict(); repoComment = dict(); repoCollaborator = dict()

		# user의 Event를 구하는 과정에선 repository정보가 필요하지 않기 때문에 따로 구한다.
		th1 = threading.Thread(target=repo_info.get_event, args=(userEvents,))
		th1.start(); th1.join()

		for repo_count, repo in enumerate(repo_names):
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

			open_close_issue_count = list()
			collaborator_list = list()
			repo_pullrequest = dict() # { 'OPEN/CLOSED/MERGED' : "repo/number..." }

			# user가 가지고 있는 repository별 language 정보를 가져온다.
			th2 = threading.Thread(target=repo_info.get_repo_lang, args=(repo, repoLangs,))
			# user가 가지고 있는 repository별 Topic 정보를 가져온다.
			th3 = threading.Thread(target=repo_info.get_repo_topic, args=(repo, repoTopics,))
			# user가 가지고 있는 repository별 Branch 정보를 가져온다.
			th4 = threading.Thread(target=repo_info.get_branches, args=(repo, repoBranches,))
			# user가 가지고 있는 repository별 open / close 된 issue의 count를 가져온다.
			th5 = threading.Thread(target=repo_info.get_issues, args=(repo, open_close_issue_count,))
			# user가 가진 repository별 addition_code_line / deletion_code_line의 정보를 가져온다.
			th6 = threading.Thread(target=self.commits_crawler, args=(commit_data, committed_data, repo, repo_count, repo_code_line,))
			# user가 가진 repository별 issue_comment의 count를 가져온다.
			th7 = threading.Thread(target=repo_info.get_issues_comment, args=(repo, repoComment,))
			# user가 가진 repository별 협업자들의 이름을 list의 형태로 가져온다.
			th8 = threading.Thread(target=repo_info.get_collaborators, args=(repo, collaborator_list,))
			# user가 가진 repository별 pull_request의 정보를 가져온다.
			th9 = threading.Thread(target=self.pullrequest_crawler, args=(repo_pullrequest, repo, self.user_name, self.header,))
			#------------------------------------------------------------------
			th2.start(); th3.start(); th4.start(); th5.start(); th6.start(); th7.start(); th8.start(); th9.start()
			th2.join(); th3.join(); th4.join(); th5.join(); th6.join(); th7.join(); th8.join(); th9.join()

			# ---------------------- Get -> Add about pr_number_repo_score -------------------------------
			score_board = {'MERGED' : 8, 'OPEN' : 4, 'CLOSED' : 2}
			for state in repo_pullrequest.keys():
				for num in repo_pullrequest[state].split(","):
					pr_number_crawler = graphql_api_crawler_pr_number(repo, self.header, self.user_name, num.split("/")[1])
					pr_number_data = pr_number_crawler.run_query()
					if pr_number_data['data']['repository']['pullRequest']['author'] != None and pr_number_data['data']['repository']['pullRequest']['author']['login'] == self.user_name:
						if repo not in pr_repo_score:
							pr_repo_score[repo] = score_board[state]
						else:
							pr_repo_score[repo] += score_board[state]
					else:
						for participant in pr_number_data['data']['repository']['pullRequest']['participants']['edges']:
							# repository의 pullRequest 데이터에서 참가(활동)를 했었다면 5점의 점수가 부여된다.
							if participant['node']['login'] == self.user_name:
								if repo not in pr_repo_score:
									pr_repo_score[repo] = 5
								else:
									pr_repo_score[repo] += 5
					# Add commit total count
					if repo not in pr_repo_score:
						pr_repo_score[repo] = pr_number_data['data']['repository']['pullRequest']['commits']['totalCount']
					else:
						pr_repo_score[repo] += pr_number_data['data']['repository']['pullRequest']['commits']['totalCount']
			# --------------------------------------------------------------------------------------------------------------

			#Choose the case with the highest number of commit attempts.
			if repo_data['data']['repository']['defaultBranchRef'] == None:
				continue

			if repo_data['data']['repository']['primaryLanguage'] == None:
				total_repo_info.append([repo_count, repo_data['data']['repository']['url'], repo_data['data']['repository']['stargazers']['totalCount'], repo_data['data']['repository']['watchers']['totalCount'], repo_data['data']['repository']['forkCount'], repo_data['data']['repository']['createdAt'][:10], repo_data['data']['repository']['updatedAt'][:10], repo_data['data']['repository']['description'], "No_Lang"])
			else:
				total_repo_info.append([repo_count, repo_data['data']['repository']['url'], repo_data['data']['repository']['stargazers']['totalCount'], repo_data['data']['repository']['watchers']['totalCount'], repo_data['data']['repository']['forkCount'], repo_data['data']['repository']['createdAt'][:10], repo_data['data']['repository']['updatedAt'][:10], repo_data['data']['repository']['description'], repo_data['data']['repository']['primaryLanguage']['name']])

			commit_ranking[repo_count] = repo_data['data']['repository']['defaultBranchRef']['target']['history']['totalCount']

			repo_names_dict[repo_count] = repo
			open_close_issue_count.append(issue_open_totalCount)
			open_close_issue_count.append(issue_closed_totalCount)
			repoIssue[repo] = open_close_issue_count

			repoCollaborator[repo] = collaborator_list

		#print(open_close_issue_count)
		#print(self.repoIssue) # { repo_name: [personal open issue, personal close issue, total open issue, total close issue] }
		#print(self.repoCollaborator)
		#print(self.self.repoCommit_info) # { number: { date: [addition, deletion] } }
		#print(commit_ranking) # { number: commit_count }
		#print(repo_names_dict) # { number: repository_name }
		#print(self.repoComment)
		#print(pr_repo_score) # 점수가 뽑히긴 하는데 그 과정이 상당히 오래걸린다.

		#Repository 4개 선정 과정. --------------------------------------------------------------------------------------------------------------------------------------------
			# [1] master를 제외한 branch를 사용한 것을 최고 우선순위로 정한다.
				# [1.1] 4개를 넘었을 경우 : 종합 점수를 내어 4개를 정한다.
				# [1.2] 4개를 넘지 못했을 경우 : Branch를 사용하지 않은 repository 중 높은 점수로 나머지를 채운다.
			# [2] Collaborator들의 여부에 따라 점수로 변경한다. (혼자 진행할 경우 우선순위에서 제외시킬려고 했지만 학생들의 경우 Repository가 없을 수도 있기에 점수로 변경)
				# [2.1] Collaborator의 수에 따라 1점씩 준다.
			# [3] License 여부에 따라 점수로 변경한다. (License 사용 또한 github사용의 큰 의미를 둔다고 생각)
				# [3.1] License가 있다면 1점, 없다면 0점을 준다.
			# [4] 개인 commit / 전체 commit 을 계산하여 점수로 변경한다.
			# [5] 개인 issue / 전체 issue 를 계산하여 점수로 변경한다.
			# [6] 자신이 올린 issue를 제외한 issue에 comment를 단 횟수에 따라 점수로 변경한다.
			# [7] pullRequest를 확인한다.
				# [7.1] 직접 올린 pullRequest라면 MERGED > OPEN > CLOSED 순으로 점수를 준다. (MERGED : 8, OPEN : 4, CLOSED : 2)
				# [7.2] 직접 올리지 않았다면 participants에 사용자가 포함되었는지 확인한다. (포함되었다면 5점을 부여한다.)
				# [7.3] pullRequest마다 실행한 commit_count를 점수에 추가한다.
		#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
		selected_repo = dict() # 선택된 repository들을 담는 dictionary
		all_repo_score = dict()
		for rn in list(repo_names_dict.values()):
			all_repo_score[rn] = 0 # Repository의 이름을 나열 => 초기 값은 0으로 설정
		#repository 4개 선정 과정 [4]
		commit_score = dict()
		for cr in list(commit_ranking.keys()):
			commit_score[cr] = (len(self.repoCommit_info[cr].keys()) / commit_ranking[cr]) # 전체 repository를 대상으로 (개인 commit / 전체 commit) 을 계산
		#repository 4개 선정 과정 [5]
		issue_score = dict()
		for ri in list(repoIssue.keys()):
			if (repoIssue[ri][2] + repoIssue[ri][3]) == 0: # division by zero error exception
				issue_score[ri] = 0
			else:
				issue_score[ri] = (repoIssue[ri][0] + repoIssue[ri][1]) / (repoIssue[ri][2] + repoIssue[ri][3])
				# issue 선정기준은 open + close의 개인 / 전체를 계산하였다. 필요하면 분리가능
		#--------------------------------------------------------------
		#repository 4개 선정 과정 [6]의 경우 self.repoComment에서 분류가 되어 값이 들어감
		#--------------------------------------------------------------
		#repository 4개 선정 과정 [2]
		for name in all_repo_score:
			if name in list(repoCollaborator.keys()):
				all_repo_score[name] += len(repoCollaborator[name])
			#repository 4개 선정 과정 [3]
			if name in list(repo_licenses.keys()):
				all_repo_score[name] += 1
			#repository 4개 선정 과정 [4] 계산
			for k, rn in enumerate(repo_names_dict.values()):
				if rn == name:
					all_repo_score[name] += commit_score[k]
			#repository 4개 선정 과정 [5] 계산
			all_repo_score[name] += issue_score[name]
			#repository 4개 선정 과정 [6] 계산
			all_repo_score[name] += repoComment[name]

		# repository 4개 선정 과정 [1]
		for br in repoBranches:
			if repoBranches[br] == True:
				selected_repo[br] = all_repo_score[br]
				del all_repo_score[br] #선택된 repository는 삭제
		if len(selected_repo) < 4: # 선택된 repository가 4개가 아닐 경우
		# Branch를 사용하지 않은 repository 중 높은 점수로 나머지를 채운다.
			leave_count = 4 - len(selected_repo)
			sorted_all_repo_score = sorted(all_repo_score.items(), key=lambda x: x[1], reverse=True) # 점수가 높은 순으로 정렬
			for lc in range(leave_count):
				selected_repo[sorted_all_repo_score[lc][0]] = sorted_all_repo_score[lc][1]

		# Add score selected_repo in pullRequest score
		for pr in list(pr_repo_score.keys()):
			if pr in list(selected_repo.keys()):
				selected_repo[pr] += pr_repo_score[pr] # 선정된 기존 repo에서 pr에 대한 점수 더하기

		selected_repo = sorted(selected_repo.items(), key=lambda x: x[1], reverse=True)
		select_repo_score = dict()
		selected_repo_codeline = dict()
		for j, sr in enumerate(selected_repo):
			if j == 4:
				break # 4개가 들어갈 경우 break
			select_repo_score[sr[0]] = sr[1]
			selected_repo_codeline[sr[0]] = repo_code_line[sr[0]]
		#print(select_repo_score) # 선정된 repository 4개

		return repo_names_dict, total_repo_info, select_repo_score, repoLangs, repoTopics, userEvents, repoBranches, repoIssue, repoComment, selected_repo_codeline
		# 현재 self.repoBranches, self.repoIssue, self.repoComment -> branch / issue / issue_comment 가 main.py로 넘어가고 있다. 현재 사용은 하지 않고 있으며, 나중에 필요하면 쓸려고 넘긴듯...
