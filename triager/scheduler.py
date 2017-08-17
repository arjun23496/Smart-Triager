import pandas as pd

from utility.CouchInterface import CouchInterface
from utility.custom_output import CustomOutput
from utility.custom_output import cprint
from mappings.Ticket import csv_mapping
from openpyxl import load_workbook

import transformations

import datetime
import progressbar
import os
import re
import sys
import traceback
import json
import copy


def clean_name_index(x):
	x= x.upper()
	if x[:3] == '[O]':
		x = x[4:]
	x = x.replace('.','')
	
	x = x.strip()
	x = re.sub(' +',' ',x)
	return x

def execute(date_now, debug=True, thread=False, socketio=None, output_mode=2):

	# TODO: Change in production
	# date_now = datetime.datetime.now()
	#2016-12-21
	coutput = CustomOutput(thread=thread, socketio=socketio)

	ticket_dtime_format = "%Y-%m-%d-%H.%M.%S"

	priority_setting = [ 'severity', 'status' ]

	date_param = date_now['year']+"-"+date_now['month']+"-"+date_now['date']

	coutput.cprint("Executing scheduler", 'status_update', mode=output_mode)
	coutput.cprint("date: "+date_param, 'status_update', mode=output_mode)

	user_availability = {
		"full_day": 8,
		"half_day": 4
	}

	backlog_req = 2

	skill_level_mapping = {
		"Beginner": 3,
		"Intermediate": 2,
		"Expert": 1
	}

	skills = []

	permitted_categories = [ 'S - Map Change', 'S - Mapping Request', 'S - Map Research', 'S - PER - New Map', 'S - PER - Map Change' ]

	category_time_requirements = {
		'S - Map Change': 4,			#2-4
		'S - Mapping Request': 4,		#2-4
		'S - Map Research': 2,			#1-2
		'S - PER - New Map': 8,			#6-8
		'S - PER - Map Change': 6		#4-6
	}

	not_available_legend = ['N','V','E','O','S','C']
	half_day_legend = ['H','C']

	file_paths = {
		"backlog": "./data/backlog.csv",
		"utilization": "./data/utilization.csv",
		"skills_tracker": "./data/skills_tracker.csv",
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

	#DataStructures for report
	category_report = {
		"New Map": 0,
		"PER Map Change": 0,
		"Change": 0,
		"Research": 0
	}

	backlog_report_report = {
		"Sev 1": 0,
		"Sev 2": 0,
		"Sev 3": 0,
		"Sev 4": 0
	}

	triage_summary_report = {
		"date": "",
		"priority_deliverables": 0,
		"available_members": 0,
		"number_new_maps": 0,
		"backlog_report": {},
		"category_report": {},
		"total_allocated": 0
	}

	triage_summary_report['date'] = date_now['date']+'/'+date_now['month']+'/'+date_now['year']


	ticket_report = {
		"customer": "",
		"severity": "",
		"category": "",
		"status": "",
		"triage_recommendation": "",
		"last_worked_by": "",
		"backlog": False
	}

	all_ticket_report = {}

	#System start

	completed_tickets = []

	employee_status = {}
	available_employees = 0
	skills_tracker = None	#Populate with all the skills of employees

	couch_handle = CouchInterface()
	backlog_report_df = None
	utilization_df = None
	skills_tracker_df = None
	vacation_plan_df = None
	df = pd.DataFrame(couch_handle.document_by_assigned(False))

	if df.shape[0] <= 0:
		coutput.cprint("No tickets for the given day", 'status_update', mode=output_mode)
		coutput.cprint("Exiting....", 'status_update', mode=output_mode)
		return

	coutput.cprint("---------------Executing Transformations------------", 'status_update', mode=output_mode)

	bar = progressbar.ProgressBar(maxval=df.shape[0], widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
	bar.start()

	# print pd.unique(df['ticket_number'])

	for index,row in df.iterrows():

		temp = {}
		temp = row
		if row['triage_recommendation'] == None:
			df.set_value(index, 'triage_recommendation', "")
			row['triage_recommendation'] = ""

		if row['new_queue']=='' or pd.isnull(row['new_queue']):
			temp['new_queue']=transformations.new_value_imputer(df,index,row['ticket_number'])
			df.set_value(index, 'new queue', temp['new_queue'])

		tempcat = row['category']
		if row['category']=='' or pd.isnull(row['category']) or row['category'] not in permitted_categories:
			if debug:
				coutput.cprint("Ticket Number: "+row['ticket_number'], 'status_update', mode=output_mode)
			if row['category'] not in permitted_categories and row['category']!='' and (not pd.isnull(row['category'])):
				if debug:
					coutput.cprint("\n\nUnknown Categories encountered... Please check the Ticket List...", 'status_update', mode=output_mode)
					coutput.cprint(row['category'], 'status_update', mode=output_mode)
			if debug:
				coutput.cprint("Imputing Category", 'status_update', mode=output_mode)
			temp['category']=transformations.category_imputer(df,index,row['ticket_number'],row['action_date'],ticket_dtime_format)
			df.set_value(index, 'category', temp['category'])
			triage_reco = row['triage_recommendation']
			triage_reco += "Category determined by triager. "
			df.set_value(index, 'triage_recommendation', triage_reco)
			tempcat = temp['category']
			if debug:
				coutput.cprint("New Category: "+temp['category'], 'status_update', mode=output_mode)

		if row['severity']=='' or pd.isnull(row['severity']):
			if debug:
				coutput.cprint("Ticket Number: "+row['ticket_number'], 'status_update', mode=output_mode)
				coutput.cprint("Imputing Severity", 'status_update', mode=output_mode)
			temp['severity']=transformations.severity_imputer(df,index)
			df.set_value(index, 'severity', temp['severity'])

			triage_reco = row['triage_recommendation']
			triage_reco += "Severity determined by triager. "
			df.set_value(index, 'triage_recommendation', triage_reco)
			if debug:
				coutput.cprint("New Severity: "+temp['severity'], 'status_update', mode=output_mode)

		bar.update(index)

		if temp['category'] not in permitted_categories:
			coutput.cprint("\n\nUnknown Categories encountered... Please check the Ticket List...", 'status_update', mode=output_mode)
			coutput.cprint("Category: "+temp['category'], 'status_update', mode=output_mode)
			coutput.cprint("exiting.....", 'status_update', mode=output_mode)
			return

	bar.finish()

	coutput.cprint("Transformations Complete", 'status_update', mode=output_mode)

	coutput.cprint("---------------Checking file requirements------------", 'status_update', mode=output_mode)

	status = True

	if os.path.isfile(file_paths['utilization']):
		coutput.cprint("*Utilization Report - Found", 'status_update', mode=output_mode)
	else:
		coutput.cprint("*Utilization Report not found", "error", mode=output_mode)

	if os.path.isfile(file_paths['skills_tracker']):
		coutput.cprint("*Skills Tracker - Found", 'status_update', mode=output_mode)
		coutput.cprint("	Reading skills...", 'status_update', mode=output_mode)
		skills_tracker = pd.read_csv(file_paths['skills_tracker'])
		skills_tracker['LEVEL'] = skills_tracker['LEVEL'].apply(lambda x: skill_level_mapping[x])
		skills = pd.unique(skills_tracker['TYPE'])
		coutput.cprint("	Skill Tracker Read - Complete", 'status_update', mode=output_mode)
	else:
		coutput.cprint("*Skills Tracker not found", 'status_update', mode=output_mode)
		status = False

	if os.path.isfile(file_paths['vacation_plan']):
		coutput.cprint("*Vacation Plan - Found", 'status_update', mode=output_mode)
		coutput.cprint("	Reading Vacation Plan...", 'status_update', mode=output_mode)
		vacation_plan_df = pd.read_csv(file_paths['vacation_plan'], header=4)
		# print vacation_plan_df

		for index,row in vacation_plan_df.iterrows():
			if not pd.isnull(row[' [o] = Owner']):
				# print employee_status
				monthi = int(date_now['month'])-1
				coli = str(int(str(date_now['date'])))

				if monthi != 0:
					coli = coli+"."+str(monthi)
				# print row

				temp_tracker = skills_tracker[skills_tracker['NAME'] == row[' [o] = Owner']]

				if temp_tracker.shape[0] <= 0 or temp_tracker[temp_tracker['TYPE'] == 'Sterling Integrator (SI)'].shape[0] <=0:
					temp_df_stracker = pd.DataFrame([[row[' [o] = Owner'], 'Product', 'Sterling Integrator (SI)', 'Beginner', ' ', '2016', '-']], columns=['NAME','SKILL','TYPE','LEVEL','EXPERIENCE','LAST WORKED','CLIENTS'])
					skills_tracker = skills_tracker.append(temp_df_stracker, ignore_index = True)

				try:
					employee_status[row[' [o] = Owner']]
				except KeyError:
					employee_status[row[' [o] = Owner']] = {}
					employee_status[row[' [o] = Owner']]['tickets'] = []

				if row[coli]=='P':
					employee_status[row[' [o] = Owner']]['total_availability'] = 0
				elif row[coli] in not_available_legend:
					employee_status[row[' [o] = Owner']]['total_availability'] = 0
				elif row[coli] in half_day_legend:
					employee_status[row[' [o] = Owner']]['total_availability'] = user_availability['half_day']
				else:
					employee_status[row[' [o] = Owner']]['total_availability'] = user_availability['full_day']
				employee_status[row[' [o] = Owner']]['usage'] = 0

		coutput.cprint("	Vacation Plan Read - Complete ", 'status_update', mode=output_mode)
	else:
		coutput.cprint("*Vacation Plan not found", 'error', mode=output_mode)
		status = False

	if os.path.isfile(file_paths['backlog']):
		coutput.cprint("*Backlog Report - Found", 'status_update', mode=output_mode)
		blog_report = pd.read_csv(file_paths['backlog'], header=2)
		
		pattern = re.compile(r'.*\[S-MAP-IN\] (.*)')
		
		xindex = 0
		blog_columns = []
		for x in blog_report.columns:
			print x
			print blog_report.columns[xindex]
			blog_columns.append(csv_mapping[x])
			xindex+=1
		blog_report.columns = blog_columns
		for index,row in blog_report.iterrows():
			# print row
			# print row
			if row.isnull()['assigned_to_csr']:
				continue

			csr_person = re.search(pattern,row['assigned_to_csr'])

			if csr_person == None:
				continue

			csr_person = csr_person.group(1)
			print csr_person

			try:
				employee_status[csr_person]
				if employee_status[csr_person]['total_availability'] <= 0:
					ticket_report['triage_recommendation'] = csr_person+" is on leave. Please reassign."
			except KeyError:
				employee_status[csr_person] = {}
				employee_status[csr_person]['tickets'] = []
				employee_status[csr_person]['usage'] = -1
				employee_status[csr_person]['total_availability'] = -1
			
			dict_obj = {}
			for x in blog_columns:
				dict_obj[x] = row[x]

			dict_obj['backlog'] = True
			employee_status[csr_person]['tickets'].append(copy.deepcopy(dict_obj))

			ticket_report['severity'] = row['severity']
			# ticket_report['category'] = row['category']
			ticket_report['status'] = row['status']
			ticket_report['backlog'] = True

			all_ticket_report[row['ticket_number']] = copy.deepcopy(ticket_report)

			backlog_report_report[row['severity']]+=1

		# 	try:
		# 		employee_status[csr_person]['total_availability'] -= 2
		# 		if employee_status[csr_person]['total_availability'] < 0:
		# 			employee_status[csr_person]['total_availability'] = 0
		# 	except KeyError:
		# 		if debug:
		# 			coutput.cprint('No data found for backlog report employee '+csr_person, 'status_update', mode=output_mode)

	else:
		coutput.cprint("*Backlog Report not found", 'error', mode=output_mode)
		status = False

	triage_summary_report['backlog_report'] = backlog_report_report

	# print employee_status

	# return

	if not status:
		return

	coutput.cprint("---------------Processing-------------", 'status_update', mode=output_mode)

	# df_nr = df[df['status']=='Needs Reply']

	status_priority = [1,2]

	def filter_prior(x):
		if x == 'Needs Reply':
			return status_priority[0]
		else:
			return status_priority[1]

	def severity_prior(x):
		priority = {
			"Sev 1": 1,
			"Sev 2": 2,
			"Sev 3": 3,
			"Sev 4": 4
		}
		return priority[x]


	if debug:
		coutput.cprint("Assigning priority", 'status_update', mode=output_mode)

	df_nr = df.copy()
	df_nr['status_sort'] = df_nr['status']
	df_nr['severity_sort'] = df_nr['severity']
	df_nr['status_sort'] = df_nr['status_sort'].apply(filter_prior)
	df_nr['severity_sort'] = df_nr['severity_sort'].apply(severity_prior)

	df_nr['status_sort'] = df_nr['status_sort']*10 + df_nr['severity_sort']

	# df_nr = df_nr[df['status'] != 'Closed']

	#Ticket Assigning priority setting

	if debug:
		coutput.cprint("Priority assignment complete", 'status_update', mode=output_mode)

	if debug:
		coutput.cprint("Arranging according to priority", 'status_update', mode=output_mode)

	# df_nr.sort_values(priority_setting[0])
	
	if priority_setting[0] == 'status':
		level1_val = status_priority
	else:
		level1_val = ['Sev 1','Sev 2','Sev 3','Sev 4']

	temp_df = pd.DataFrame([], columns=df_nr.columns)

	# for x in level1_val:
	# 	temp_df = temp_df.append(df_nr[df_nr[priority_setting[0]] == x].sort_values(priority_setting[1]))

	# df_nr_severity = df_nr.sort_values('status')
	
	# if debug:
	# 	print temp_df[['status','severity','ticket_number']]

	df_nr_severity = temp_df	

	skills_tracker = skills_tracker.sort_values('LEVEL')
	# print skills_tracker

	if debug:
		coutput.cprint("Sort by priority complete", 'status_update', mode=output_mode)

	all_ticket_no = pd.unique(df[df['status'] != 'Closed']['ticket_number'])
	all_ticket_no = pd.unique(df['ticket_number'])
	total_tickets = len(all_ticket_no)
	number_of_assigned = 0

	pattern = re.compile(r'.*\[S-MAP-IN\] (.*)')
	# for index,row in df_nr.iterrows():

	#Sorting according to severity

	ttemp_df = pd.DataFrame([], columns=df_nr.columns)

	for t_no in all_ticket_no:

		df_temp_new = df_nr[df_nr['ticket_number'] == t_no]

		row = {}
		maxdate = ""

		for tindex, trow in df_temp_new.iterrows():
			# print tindex
			if tindex == 0 or maxdate == "":
				maxdate = datetime.datetime.strptime(trow['action_date'], ticket_dtime_format)
				row = trow
			else:
				tdate = datetime.datetime.strptime(trow['action_date'], ticket_dtime_format)

				if maxdate < tdate:
					maxdate = tdate
					row = trow

		ttemp_df = ttemp_df.append(pd.DataFrame([row], columns=df_nr.columns))
		# print t_no

	ttemp_df = ttemp_df.sort_values('status_sort')

	sort_df = pd.DataFrame([], columns=df_nr.columns)

	for x in level1_val:
		sort_df = sort_df.append(ttemp_df[ttemp_df[priority_setting[0]] == x].sort_values(priority_setting[1]))

	scheduler_pointer = {}

	unassigned_tickets = []

	index = 0
	progress_res = {
		'message': 'Assigning Tickets',
		'max': total_tickets,
		'index': 0,
		'step': 1
	}

	for tindex,row in ttemp_df.iterrows():

		coutput.cprint("\n--------------------\nAssigning "+t_no, 'status_update', mode=output_mode)

		print row['severity']

		index+=1
		progress_res['index']=index
		coutput.cprint(progress_res, 'status_progress', mode=3)

		# df_temp_new = df_nr[df_nr['ticket_number'] == t_no]

		# row = {}
		# maxdate = ""

		# for tindex, trow in df_temp_new.iterrows():
		# 	# print tindex
		# 	if tindex == 0 or maxdate == "":
		# 		maxdate = datetime.datetime.strptime(trow['action_date'], ticket_dtime_format)
		# 		row = trow
		# 	else:
		# 		tdate = datetime.datetime.strptime(trow['action_date'], ticket_dtime_format)

		# 		if maxdate < tdate:
		# 			maxdate = tdate
		# 			row = trow

		if row['severity'] == "Sev 2" or row['severity'] == "Sev 1":
			triage_summary_report['priority_deliverables']+=1

		if row['category'] == 'S - Map Change':
			category_report['Change']+=1
		elif row['category'] == 'S - Map Research':
			category_report['Research']+=1
		elif row['category'] == 'S - PER - New Map':
			category_report['New Map']+=1
		elif row['category'] == 'S - PER - Map Change':
			category_report['PER Map Change']+=1

		all_ticket_report[row['ticket_number']] = copy.deepcopy(ticket_report)

		print row

		ticket_dtime = datetime.datetime.strptime(row['action_date'], ticket_dtime_format)

		# mult_ticket = False

		# if row['ticket_number'] in completed_tickets:
		# 	continue

		# for index1,row1 in df_nr.iterrows():
		# 	if row1['ticket_number'] == row['ticket_number']:
		# 		temp_dt = datetime.datetime.strptime(row1['action_date'], ticket_dtime_format)
		# 		if temp_dt > ticket_dtime:
		# 			mult_ticket = True
		# 			break

		# if mult_ticket:
		# 	continue

		assigned = False
		ticket_category = row['category']
		csr_person = re.search(pattern,row['performed_by_csr'])

		if debug:
			coutput.cprint("ticket number: "+row['ticket_number'], 'status_update', mode=output_mode)

		if csr_person != None:
			employee=csr_person.group(1)
			#Assign to person set assigned to True
			if debug:
				coutput.cprint("Trying to assing directly to "+employee, 'status_update', mode=output_mode)
			
			try:
				availability = employee_status[employee]['total_availability'] - employee_status[employee]['usage']
				# if availability >= category_time_requirements[ticket_category]:

				if employee_status[employee]['total_availability'] > 0:
					if debug:
						coutput.cprint("assigned directly to "+employee, 'status_update', mode=output_mode)
					triage_reco = row['triage_recommendation']
					triage_reco += "Assigned directly to employee. "
					row['triage_recommendation'] = triage_reco
					
					row['backlog'] = False
					employee_status[employee]['tickets'].append(row)
					employee_status[employee]['usage']+=category_time_requirements[ticket_category]
					assigned = True
				# print employee_status[employee]

			except KeyError:
				if debug:
					coutput.cprint("WARNING: No data found for "+employee+". Reassigning ticket", 'status_update', mode=output_mode)

		maxdtime = 0

		if not assigned:
			#Assign to particular csr based on availability and ticket history
			
			if debug:
				coutput.cprint("Trying to assign to employee from ticket history", 'status_update', mode=output_mode)

			employee = ''
			tpattern = re.compile(r'.*\[.*\] (.*)')
			temp_df = pd.DataFrame(couch_handle.document_by_key('ticket_number',row['ticket_number']))
			# print temp_df
			for index1,row1 in temp_df.iterrows():
				# if row1['action_date'][:10]==date_param:
				# 	break

				temp_dtime = datetime.datetime.strptime(row1['action_date'],ticket_dtime_format)

				# print "tempdtime ",temp_dtime
				# print "emp ",row1['performed_by_csr']

				if temp_dtime == None or row1['performed_by_csr'] == '':
					continue

				pre_max = False

				if temp_dtime == ticket_dtime:
					break
				elif maxdtime == 0 and (row1['performed_by_csr'] != '' or row1['performed_by_csr'] != None) :
					maxdtime = temp_dtime
					pre_max = True
				elif temp_dtime > maxdtime and (row1['performed_by_csr'] != '' or row1['performed_by_csr'] != None):
					maxdtime = temp_dtime
					pre_max = True

				if pre_max:
					# print "maximising to prev"
					csr_person = re.search(tpattern,row1['performed_by_csr'])
					# print csr_person
					if csr_person!=None:
						employee = csr_person.group(1)
			
			t = False

			if debug:
				coutput.cprint("Assiging to "+employee, 'status_update', mode=output_mode)

			try:
				availability = employee_status[employee]['total_availability'] - employee_status[employee]['usage']
				# if availability >= category_time_requirements[ticket_category]:
			
			except KeyError:
				if debug:
					coutput.cprint("Employee not present in vacation planner "+employee, 'status_update', mode=output_mode)
					t = True

			if not t:
				try:
					if employee_status[employee]['total_availability'] > 0:
						triage_reco = row['triage_recommendation']
						triage_reco += "Assigned using ticket history. "
						row['triage_recommendation'] = triage_reco
						if debug:
							coutput.cprint("assigned from history to "+employee, 'status_update', mode=output_mode)
						row['backlog'] = False
						employee_status[employee]['tickets'].append(row)
						employee_status[employee]['usage']+=category_time_requirements[ticket_category]
						assigned = True
				except KeyError:
					if debug:
						coutput.cprint("Ticket history not present", 'status_update', mode=output_mode)

		# if row['ticket_number'] == u'5377-13340579':
		# 	return

		if not assigned:
			if debug:
				coutput.cprint("Trying default scheduler model", 'status_update', mode=output_mode)
			req_skill = 'Sterling Integrator (SI)'
			for x in skills:
				reg_x = re.escape(x)
				skill_regx = re.compile(r'.*'+reg_x+'.*')

				if skill_regx.search(row['alert_comments'])!=None or skill_regx.search(row['detail'])!=None or skill_regx.search(row['comments'])!=None:
					req_skill = x

			if debug:
				coutput.cprint("Skill Required: "+req_skill, 'status_update', mode=output_mode)

			triage_reco = row['triage_recommendation']
			triage_reco += "Skill: "+req_skill+". "
			row['triage_recommendation'] = triage_reco

			##Scheduler---------------

			
			temp_skills = skills_tracker[skills_tracker['TYPE'] == req_skill]

			temp_skills = temp_skills.reset_index(drop=True)

			maxrows = temp_skills.shape[0]

			minemployee = ''
			mintickets = 0
			local_availability = 0

			for index1,row1 in temp_skills.iterrows():
				f = False
				try:
					employee_status[row1['NAME']]
				except KeyError:
					coutput.cprint("WARNING: Employee '"+row1['NAME']+"' not found in vacation planner", 'status_update', mode=output_mode)
					continue

				if employee_status[row1['NAME']]['total_availability'] > 0:
					local_availability+=1
					notickets = len(employee_status[row1['NAME']]['tickets'])
					if minemployee == '' or notickets < mintickets:
						minemployee = row1['NAME']
						mintickets = notickets

			if local_availability ==0:
				if debug:
					coutput.cprint("No employee available to assign...", 'status_update', mode=output_mode)
			else:
				row['backlog'] = False
				employee_status[minemployee]['tickets'].append(row)
				triage_reco = row['triage_recommendation']
				triage_reco += "Assigned using default scheduler model. "
				row['triage_recommendation'] = triage_reco
				coutput.cprint("Assigned to employee "+minemployee, 'status_update', mode=output_mode)
				assigned = True

		completed_tickets.append(row['ticket_number'])
		
		if not assigned:
			# print employee_status
			# return
			if debug:
				coutput.cprint("Unable to assign ticket", 'status_update', mode=output_mode)
			unassigned_tickets.append(row['ticket_number'])
		else:
			number_of_assigned += 1

		ticket_report['severity'] = row['severity']
		ticket_report['category'] = row['category']
		ticket_report['status'] = row['status']
		ticket_report['backlog'] = False
		ticket_report['triage_recommendation'] = row['triage_recommendation']
		coutput.cprint("--------------------", 'status_update', mode=output_mode)

	triage_summary_report['category_report'] = category_report

	coutput.cprint("Allocation Complete", 'status_update', mode=output_mode)
	# Utilisation Calculation
	# print "---------------------Utilization------------------------------"
	employee_status_report = copy.deepcopy(employee_status)
	for x in employee_status:
		coutput.cprint("-----------------------------------------------------", 'status_update', mode=output_mode)
		coutput.cprint("Name: "+x, 'status_update', mode=output_mode)
		if employee_status[x]['total_availability'] == 0:
			coutput.cprint("Employee not available", 'status_update', mode=output_mode)
		else:
			utilization = 100.0*employee_status[x]['usage']/employee_status[x]['total_availability']
			# print "Availability: ",employee_status[x]['total_availability']
			# print "Usage: ",employee_status[x]['usage']
			coutput.cprint("Number of tickets assigned: "+str(len(employee_status[x]['tickets'])), 'status_update', mode=output_mode)
			# print "Utilization: ",utilization,"%"
			coutput.cprint("Tickets:", 'status_update', mode=output_mode)
			ticket_list = []
			for y in employee_status[x]['tickets']:
				coutput.cprint("\t"+y['ticket_number'], 'status_update', mode=output_mode)
				ticket_list.append(y['ticket_number'])

			print x
			print ticket_list
			employee_status_report[x]['tickets'] = ';'.join(ticket_list)

	for x in employee_status:
		if employee_status[x]['total_availability'] > 0:
			available_employees+=1

	coutput.cprint("Unassigned Tickets", 'status_update', mode=output_mode)
	coutput.cprint(str(unassigned_tickets), 'status_update', mode=output_mode)

	coutput.cprint("-----------------System Status-------------------", 'status_update', mode=output_mode)
	coutput.cprint("Total tickets: "+str(total_tickets), 'status_update', mode=output_mode)
	coutput.cprint("Tickets assigned: "+str(number_of_assigned), 'status_update', mode=output_mode)
	coutput.cprint("Total employees: "+str(len(employee_status)), 'status_update', mode=output_mode)
	coutput.cprint("Employees available: "+str(available_employees), 'status_update', mode=output_mode)
	coutput.cprint("% assigned: "+str((1.0*number_of_assigned/total_tickets)*100)+"%", 'status_update', mode=output_mode)

	coutput.cprint("Creating Reports", 'status_update', mode=output_mode)	
	triage_summary_report['available_members'] = available_employees
	triage_summary_report['total_allocated'] = number_of_assigned
	with open(os.path.join(os.path.dirname(__file__),'report/triager_summary_report.json'), 'w') as fp:
		json.dump(triage_summary_report, fp)
	coutput.cprint("Triage Summary report saved", 'status_update', mode=output_mode)

	with open(os.path.join(os.path.dirname(__file__),'report/ticket_report.json'), 'w') as fp:
		json.dump(all_ticket_report, fp)
	coutput.cprint("Allocation Recommendation report saved", 'status_update', mode=output_mode)

	with open(os.path.join(os.path.dirname(__file__),'report/employee_status_report.json'), 'w') as fp:
		json.dump(employee_status_report, fp)
	coutput.cprint("Employee Status report saved", 'status_update', mode=output_mode)
	
	# print employee_status['Resource_AB']
	# print employee_status['Resource_DK']

	# print employee_status