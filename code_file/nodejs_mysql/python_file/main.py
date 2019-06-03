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
	
	new_repo_langs = dict()
	for j in repo_lang:
		percen = str(round(j[1]/Allcount*100))
		if(j[1] %  2 == 0):
			new_repo_langs[j[0]] = "c100 p" + str(percen) + " big green"
		else:
			new_repo_langs[j[0]] = "c100 p" + str(percen) + " big orange"
	return new_repo_langs

def search_info(argv):
	if len(argv) < 2:
		print("Type as shown : python3 ~/python_profile/nodejs_mysql/python_file/main.py HwangDongJun")
		sys.exit(0)

	total_data = dict() #resume작성을 위한 전체적인 data 저장하기 위한 구조체
	#etc_info = dict()
	
	user_cert = argv[1]
	user_name = argv[2]

	Ucert = git_certification(user_cert)
	cert_info = Ucert.get_info2base64()

	header = {'Authorization' : ('Basic ' + cert_info), 'Accept' : 'application/vnd.github.mercy-preview+json'} # make haeder
	info_crawler = get_info(header, user_name) #정보를 수집하는 기본적은 crawler이다.

	#user 자신의 정보를 가져온다.
	Uinfo_data = info_crawler.user_info_crawling()
	total_data['user_info'] = Uinfo_data
	#--------------------------------------------------

	#user가 가지고 있는 repository들의 정보들을 가져온다.
	repo_names, total_repo_info, commit_ranking,  repo_langs, repo_topics, user_events, repo_branches, repo_check_issue, repo_issue_comment = info_crawler.repo_info_crawling()
	
	repo_info = list()
	for i in commit_ranking:
		repo_info.append(total_repo_info[i[0]])
	total_data['repo_info'] = repo_info
	
	new_repo_names = dict()
	for j, name in enumerate(repo_info):
		new_repo_names[j] = repo_names[name[0]]
	total_data['repo_names'] = new_repo_names

	repo_langs = sorted(repo_langs.items(), key=lambda x: x[1], reverse=True)
	repo_langs = repo_langs[:6]
	#대표하는 언어를 내림차순으로 정렬한 다음 6개로 끊는다.
	new_repo_langs = avg_lang_percentage(repo_langs)

	total_data['repos_lang'] = new_repo_langs
	total_data['repos_topic'] = repo_topics
	total_data['user_event'] = user_events
	total_data['repo_branch'] = repo_branches
	total_data['repo_issue'] = repo_check_issue
	total_data['repo_comment'] = repo_issue_comment
	#---------------------------------------------------
	#print(total_data)
	
	'''
	with open("/home/dnlab/python_profile/nodejs_mysql/python_file/user_profile/info_dict_"+user_name+".json", "w", encoding="utf-8") as make_file:
		json.dump(total_data, make_file, ensure_ascii=False)
	'''
if __name__ == '__main__':
	sys.exit(search_info(sys.argv))
