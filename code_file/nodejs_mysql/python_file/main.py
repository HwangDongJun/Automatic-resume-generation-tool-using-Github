import sys
import os
import csv
import json
import math

from get_certification import git_certification
from github_info_crawler import get_info

def avg_lang_percentage(repo_lang):
	Allcount = 0
	for i in repo_lang:
		Allcount += i[1]

	sort_repo_langs = dict()
	for j in repo_lang:
		percen = str(round(j[1]/Allcount*100))
		sort_repo_langs[j[0]] = str(percen) + '%'
	return sort_repo_langs

def search_info(argv):
	if len(argv) < 2:
		print("Type as shown : python3 file_path githubid:githubpwd searchable_name")
		sys.exit(0)

	total_data = dict() # resume작성을 위한 전체적인 data 저장하기 위한 구조체
	# 저장한 data를 resume 작성을 위해 main_page.js 파일로 전달

	user_cert = argv[1] # Github_id:Github_pwd
	user_name = argv[2] # 검색하고자 하는 Github name
	Uname = argv[3] # 입력받은 user의 실제 이름

	Ucert = git_certification(user_cert)
	cert_info = Ucert.get_info2base64() # Github_id:Github_pwd를 base64의 형태로 전환

	header = {'Authorization' : ('Basic ' + cert_info), 'Accept' : 'application/vnd.github.mercy-preview+json'} # make haeder
	info_crawler = get_info(header, user_name) # 정보를 수집하는 crawler

	# user의 정보를 가져옴
	Uinfo_data = info_crawler.user_info_crawling()
	total_data['user_info'] = Uinfo_data # user의 정보를 total_data에 담는다.
	# total_data['user_info']은 [avatarUrl, bio, location, github_url, websiteUrl, company] 의 형태로 저장

	# --------------------------------------------------------------------------------------------------------------------------------------
	# 
	# --------------------------------------------------------------------------------------------------------------------------------------
	#user가 가지고 있는 repository들의 정보들을 가져온다.
	repo_names, total_repo_info, selected_repo_ranking, repo_langs, repo_topics, user_events, repo_branches, repo_check_issue, repo_issue_comment, code_lines = info_crawler.repo_info_crawling()

	repo_info = list()
	for sr in list(selected_repo_ranking.keys()): # 현재 점수는 넘기지 않고 있으며, 선택된 4개의 repository만 포함
		for tri in total_repo_info:
			if sr == tri[1].split('/')[4]:
				repo_info.append(tri)
	total_data['repo_info'] = repo_info # 선정된 4개의 repository를 Frontend로 넘겨주기 위해 total_data에 담는다.

	new_repo_names = dict()
	for j, name in enumerate(repo_info):
		new_repo_names[j] = repo_names[name[0]]
	total_data['repo_names'] = new_repo_names

	repo_langs = sorted(repo_langs.items(), key=lambda x: x[1], reverse=True)
	repo_langs = repo_langs[:6]
	#대표하는 언어를 내림차순으로 정렬한 다음 6개로 끊는다.
	sort_repo_langs = avg_lang_percentage(repo_langs)

	total_data['user_name'] = Uname
	total_data['repos_lang'] = sort_repo_langs
	total_data['repos_topic'] = repo_topics
	total_data['user_event'] = user_events
	total_data['repo_branch'] = repo_branches
	total_data['repo_issue'] = repo_check_issue
	total_data['repo_comment'] = repo_issue_comment
	total_data['code_line'] = code_lines
	#print(total_data)

	with open("C:/Users/HwangDongjun/Desktop/nodejs_mysql/python_file/user_profile/info_dict_"+user_name+".json", "w", encoding="utf-8") as make_file:
		json.dump(total_data, make_file, ensure_ascii=False)

if __name__ == '__main__':
	sys.exit(search_info(sys.argv))
