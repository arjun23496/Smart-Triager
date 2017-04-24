import pandas as pd

from utility.CouchInterface import CouchInterface
from openpyxl import load_workbook

import transformations

import datetime
import progressbar
import os
import re

def execute(date_now, debug=True):

	# TODO: Change in production
	# date_now = datetime.datetime.now()
	#2016-12-21

	priority_setting = [ 'severity', 'status' ]

	date_param = date_now['year']+"-"+date_now['month']+"-"+date_now['date']

	print "Executing scheduler"
	print "date: "+date_param

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
		"backlog": "./data/backlog_report.csv",
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

	employee_status = {}
	available_employees = 0
	skills_tracker = None	#Populate with all the skills of employees

	couch_handle = CouchInterface()
	backlog_report_df = None
	utilization_df = None
	skills_tracker_df = None
	vacation_plan_df = None
	df = pd.DataFrame(couch_handle.document_by_assigned(date_now, False))

	if df.shape[0] <= 0:
		print "No tickets for the given day"
		print "Exiting...."
		return

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

	if os.path.isfile(file_paths['utilization']):
		print "*Utilization Report - Found"
	else:
		print "*Utilization Report not found"
		status = False

	if os.path.isfile(file_paths['skills_tracker']):
		print "*Skills Tracker - Found"
		print "	Reading skills..."
		skills_tracker = pd.read_csv(file_paths['skills_tracker'])
		skills_tracker['LEVEL'] = skills_tracker['LEVEL'].apply(lambda x: skill_level_mapping[x])
		skills = pd.unique(skills_tracker['TYPE'])
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

				if skills_tracker[skills_tracker['NAME'] == row[' [o] = Owner']].shape[0] <= 0:
					continue

				try:
					employee_status[row[' [o] = Owner']]
				except KeyError:
					employee_status[row[' [o] = Owner']] = {}
					employee_status[row[' [o] = Owner']]['tickets'] = []

				if row[coli]=='P':
					print "Public Holiday. Exiting...."
				elif row[coli] in not_available_legend:
					employee_status[row[' [o] = Owner']]['total_availability'] = 0
				elif row[coli] in half_day_legend:
					employee_status[row[' [o] = Owner']]['total_availability'] = user_availability['half_day']
				else:
					employee_status[row[' [o] = Owner']]['total_availability'] = user_availability['full_day']
				employee_status[row[' [o] = Owner']]['usage'] = 0

		print "	Vacation Plan Read - Complete "
	else:
		print "*Vacation Plan not found"
		status = False

	# print employee_status

	if os.path.isfile(file_paths['backlog']):
		print "*Backlog Report - Found"
		blog_report = pd.read_csv(file_paths['backlog'], skiprows=3)
		
		pattern = re.compile(r'.*\[S-MAP-IN\] (.*)')
		
		for index,row in blog_report.iterrows():
			if row.isnull()['Assigned To (CSR)']:
				continue			

			csr_person = re.search(pattern,row['Assigned To (CSR)'])

			if csr_person == None:
				continue

			csr_person = csr_person.group(1)

			try:
				employee_status[csr_person]['total_availability'] -= 2
				if employee_status[csr_person]['total_availability'] < 0:
					employee_status[csr_person]['total_availability'] = 0
			except KeyError:
				if debug:
					print 'No data found for backlog report employee ',csr_person

	else:
		print "*Backlog Report not found"
		status = False


	print "---------------Allocating for Needs Reply queue and [SMAP-IN]-----"

	# df_nr = df[df['status']=='Needs Reply']

	status_priority = [1,2]

	def filter_prior(x):
		if x == 'Needs Reply':
			return status_priority[0]
		else:
			return status_priority[1]

	df_nr = df.copy()
	df_nr['status'] = df_nr['status'].apply(filter_prior)

	#Ticket Assigning priority setting

	df_nr.sort_values(priority_setting[0])
	
	if priority_setting[0] == 'status':
		level1_val = status_priority
	else:
		level1_val = ['Sev 1','Sev 2','Sev 3','Sev 4']

	temp_df = pd.DataFrame([], columns=df_nr.columns)

	for x in level1_val:
		temp_df = temp_df.append(df_nr[df_nr[priority_setting[0]] == x].sort_values(priority_setting[1]))

	# df_nr_severity = df_nr.sort_values('status')
	
	if debug:
		print temp_df[['status','severity','ticket_number']]

	df_nr_severity = temp_df	

	skills_tracker = skills_tracker.sort_values('LEVEL')
	# print skills_tracker

	total_tickets = df_nr.shape[0]
	number_of_assigned = 0

	print employee_status

	pattern = re.compile(r'.*\[S-MAP-IN\] (.*)')
	for index,row in df_nr.iterrows():
		assigned = False
		ticket_category = row['category']
		csr_person = re.search(pattern,row['performed_by_csr'])
		
		if debug:
			print "ticket number: ",row['ticket_number']

		if csr_person != None:
			employee=csr_person.group(1)
			#Assign to person set assigned to True
			
			try:
				availability = employee_status[employee]['total_availability'] - employee_status[employee]['usage']
				if availability >= category_time_requirements[ticket_category]:
					if debug:
						print "assigned directly to ",employee
					employee_status[employee]['tickets'].append(row)
					employee_status[employee]['usage']+=category_time_requirements[ticket_category]
					assigned = True
				# print employee_status[employee]

			except KeyError:
				if debug:
					print "WARNING: No data found for ",employee,". Reassigning ticket"

		if not assigned:
			#Assign to particular csr based on availability and ticket history
			employee = ''
			temp_df = pd.DataFrame(couch_handle.document_by_key('ticket_number',row['ticket_number']))
			for index1,row1 in temp_df.iterrows():
				if row1['action_date'][:10]==date_param:
					break
				csr_person = re.search(pattern,row1['performed_by_csr'])
				if csr_person!=None:
					employee = csr_person.group(1)
			
			try:
				availability = employee_status[employee]['total_availability'] - employee_status[employee]['usage']
				if availability >= category_time_requirements[ticket_category]:
					if debug:
						print "assigned from history to ",employee
					employee_status[employee]['tickets'].append(row)
					employee_status[employee]['usage']+=category_time_requirements[ticket_category]
					assigned = True
			except KeyError:
				if debug:
					print "Ticket history not present"

		if not assigned:
			req_skill = 'Sterling Integrator (SI)'
			for x in skills:
				reg_x = re.escape(x)
				skill_regx = re.compile(r'.*'+reg_x+'.*')

				if skill_regx.search(row['alert_comments'])!=None or skill_regx.search(row['detail'])!=None or skill_regx.search(row['comments'])!=None:
					req_skill = x

			if debug:
				print "Skill Required: ",req_skill

			##Scheduler---------------

			temp_skills = skills_tracker[skills_tracker['TYPE'] == req_skill]

			for i,r in temp_skills.iterrows():
				employee = r['NAME']
				try:
					availability = employee_status[employee]['total_availability'] - employee_status[employee]['usage']
					if availability >= category_time_requirements[ticket_category]:
						if debug:
							print "assigned using scheduler to ",employee
						employee_status[employee]['tickets'].append(row)
						employee_status[employee]['usage']+=category_time_requirements[ticket_category]
						assigned = True
						break

				except KeyError:
					pass
				# print "WARNING: No data found for ",employee,". Reassigning ticket"
		
		if not assigned:
			if debug:
				print "Unable to assign ticket"
		else:
			number_of_assigned += 1

	print "Allocation Complete"
	# Utilisation Calculation
	# print "---------------------Utilization------------------------------"
	for x in employee_status:
		print "-----------------------------------------------------"
		print "Name: ",x
		if employee_status[x]['total_availability'] == 0:
			print "Employee not available"
		else:
			utilization = 100.0*employee_status[x]['usage']/employee_status[x]['total_availability']
			print "Availability: ",employee_status[x]['total_availability']
			print "Usage: ",employee_status[x]['usage']
			print "Number of tickets assigned: ",len(employee_status[x]['tickets'])
			print "Utilization: ",utilization,"%"
			print "Tickets:"
			for x in employee_status[x]['tickets']:
				print "\t",x['ticket_number']

	for x in employee_status:
		if employee_status[x]['total_availability'] > 0:
			available_employees+=1

	print "-----------------System Status-------------------"
	print "Total tickets: ",total_tickets
	print "Tickets assigned: ",number_of_assigned
	print "Total employees: ",len(employee_status)
	print "Employees available: ",available_employees
	print "% assigned: ",((1.0*number_of_assigned/total_tickets)*100),"%"

	# print employee_status