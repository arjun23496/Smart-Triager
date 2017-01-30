import pandas as pd

from utility.CouchInterface import CouchInterface
from openpyxl import load_workbook

import transformations

import datetime
import progressbar
import os
import re

def execute():

	# date_now = datetime.datetime.now()
	date_now = {
		"year": "2016",
		"date": "13",
		"month": "1"
	}

	file_paths = {
		"backlog": "./data/backlog_report.csv",
		"utilization": "./data/utilization.csv",
		"skills_tracker": "./data/skills_tracker.json",
		"vacation_plan": "./data/vacation_plan.csv"
	}

	months_mapping = {
		"jan": "",
		"feb": "1",
		"mar": "2",
		"apr": "3",
		"may": "4",
		"jun": "5",
		"jul": "6",
		"aug": "7",
		"sep": "8",
		"oct": "9",
		"nov": "10",
		"dec": "11"
	}

	vacation_plan = {}	#Populate with present day vacation plan
	skills_tracker = None	#Populate with all the skills of employees

	couch_handle = CouchInterface()
	backlog_report_df = None
	utilization_df = None
	skills_tracker_df = None
	vacation_plan_df = None
	df = pd.DataFrame(couch_handle.document_by_assigned(False))

	print "---------------Executing Transformations------------"

	bar = progressbar.ProgressBar(maxval=df.shape[0], widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
	bar.start()

	for index,row in df.iterrows():
		temp = {}
		temp = row
		if row['new_queue']=='' or pd.isnull(row['new_queue']):
			temp['new_queue']=transformations.new_value_imputer(df,index,row['ticket_number'])
		if row['category']=='' or pd.isnull(row['category']):
			temp['category']=transformations.category_imputer(df,index)
		if row['severity']=='' or pd.isnull(row['severity']):
			temp['severity']=transformations.severity_imputer(df,index)
		bar.update(index)

	bar.finish()

	print "Transformations Complete"

	print "---------------Checking file requirements------------"

	status = True
	if os.path.isfile(file_paths['backlog']):
		print "*Backlog Report - Found"
	else:
		print "*Backlog Report not found"
		status = False

	if os.path.isfile(file_paths['utilization']):
		print "*Utilization Report - Found"
	else:
		print "*Utilization Report not found"
		status = False

	if os.path.isfile(file_paths['skills_tracker']):
		print "*Skills Tracker - Found"
		print "	Reading skills..."
		skills_tracker = pd.read_json(file_paths['skills_tracker'])
		print "	Skill Tracker Read - Complete"
	else:
		print "*Skills Tracker not found"
		status = False

	if os.path.isfile(file_paths['vacation_plan']):
		print "*Vacation Plan - Found"
		print "	Reading Vacation Plan..."
		vacation_plan_df = pd.read_csv(file_paths['vacation_plan'], header=4)

		for index,row in vacation_plan_df.iterrows():
			if not pd.isnull(row[' [o] = Owner']):
				monthi = int(date_now['month'])-1
				coli = str(date_now['date'])
				if monthi != 0:
					coli = coli+"."+str(monthi)
				vacation_plan[row[' [o] = Owner']] = row[coli]
		print "	Vacation Plan Read - Complete "
	else:
		print "*Vacation Plan not found"
		status = False

	print "---------------Allocating for Needs Reply queue and [SMAP-IN]-----"

	df_nr = df[df['status']=='Needs Reply']

	pattern = re.compile(r'.*\[S-MAP-IN\] (.*)')
	for index,row in df_nr.iterrows():
		csr_person = re.search(pattern,row['performed_by_csr'])
		if csr_person != None:
			# print csr_person.group(1)
			pass

	print skills_tracker.head()