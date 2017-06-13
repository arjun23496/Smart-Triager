import pandas as pd

from utility.CouchInterface import CouchInterface
from openpyxl import load_workbook

import transformations

import datetime
import progressbar
import os
import re

def clean_name_index(x):
	x= x.upper()
	if x[:3] == '[O]':
		x = x[4:]
	x = x.replace('.','')
	
	x = x.strip()
	x = re.sub(' +',' ',x)
	return x

def execute(date_now, debug=True):

	# TODO: Change in production
	# date_now = datetime.datetime.now()
	#2016-12-21

	ticket_dtime_format = "%Y-%m-%d-%H.%M.%S"

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
		print "No tickets for the given day"
		print "Exiting...."
		return [True, None]

	print "---------------Executing Transformations------------"

	bar = progressbar.ProgressBar(maxval=df.shape[0], widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
	bar.start()

	print pd.unique(df['ticket_number'])

	for index,row in df.iterrows():
		temp = {}
		temp = row
		if row['new_queue']=='' or pd.isnull(row['new_queue']):
			temp['new_queue']=transformations.new_value_imputer(df,index,row['ticket_number'])
			df.set_value(index, 'new queue', temp['new_queue'])

		if row['category']=='' or pd.isnull(row['category']) or row['category'] not in permitted_categories:
			if debug:
				print "Ticket Number: ",row['ticket_number']
			if row['category'] not in permitted_categories and row['category']!='' and (not pd.isnull(row['category'])):
				if debug:	
					print "\n\nUnknown Categories encountered... Please check the Ticket List..."
					print row['category']
			if debug:
				print "Imputing Category"
			temp['category']=transformations.category_imputer(df,index)
			df.set_value(index, 'category', temp['category'])
			if debug:
				print "New Category: ",temp['category']

		if row['severity']=='' or pd.isnull(row['severity']):
			if debug:
				print "Ticket Number: ",row['ticket_number']
				print "Imputing Severity"
			temp['severity']=transformations.severity_imputer(df,index)
			df.set_value(index, 'severity', temp['severity'])
			if debug:
				print "New Severity: ",temp['severity']

		bar.update(index)

		if temp['category'] not in permitted_categories:
			print "\n\nUnknown Categories encountered... Please check the Ticket List..."
			print "Category: ",temp['category']
			print "exiting....."
			return [ False, None ]

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
		skills_tracker['NAME'] = skills_tracker['NAME'].apply(lambda x: clean_name_index(x))
		skills = pd.unique(skills_tracker['TYPE'])
		print "	Skill Tracker Read - Complete"
		# print skills_tracker
	else:
		print "*Skills Tracker not found"
		status = False

	if os.path.isfile(file_paths['vacation_plan']):
		print "*Vacation Plan - Found"
		print "	Reading Vacation Plan..."
		vacation_plan_df = pd.read_csv(file_paths['vacation_plan'], header=4)
		# print vacation_plan_df

		for index,row in vacation_plan_df.iterrows():
			if not pd.isnull(row[' [o] = Owner']):
				# print employee_status
				monthi = int(date_now['month'])-1
				coli = str(date_now['date'])
				if monthi != 0:
					coli = coli+"."+str(monthi)

				emp_status_key = clean_name_index(row[' [o] = Owner'])
				if emp_status_key[:3] == '[O]':
					emp_status_key = emp_status_key[4:]

				if skills_tracker[skills_tracker['NAME'] == emp_status_key].shape[0] <= 0:
					print "Appending ",emp_status_key
					temp_df_stracker = pd.DataFrame([[emp_status_key, 'Product', 'Sterling Integrator (SI)', 'Beginner', ' ', '2016', '-']], columns=['NAME','SKILL','TYPE','LEVEL','EXPERIENCE','LAST WORKED','CLIENTS'])
					skills_tracker = skills_tracker.append(temp_df_stracker, ignore_index = True)
					# continue

				try:
					employee_status[emp_status_key]
				except KeyError:
					employee_status[emp_status_key] = {}
					employee_status[emp_status_key]['tickets'] = []

				if row[coli]=='P':
					employee_status[emp_status_key]['total_availability'] = 0
				elif row[coli] in not_available_legend:
					employee_status[emp_status_key]['total_availability'] = 0
				elif row[coli] in half_day_legend:
					employee_status[emp_status_key]['total_availability'] = user_availability['half_day']
				else:
					employee_status[emp_status_key]['total_availability'] = user_availability['full_day']
				employee_status[emp_status_key]['usage'] = 0

		print "	Vacation Plan Read - Complete "
	else:
		print "*Vacation Plan not found"
		status = False

	# print employee_status
	# print skills_tracker
	# return True

	if os.path.isfile(file_paths['backlog']):
		print "*Backlog Report - Found"
		blog_report = pd.read_csv(file_paths['backlog'])
		
		pattern = re.compile(r'.*\[S-MAP-IN\] (.*)')
		
		# print blog_report.columns
		for index,row in blog_report.iterrows():
			# print row
			# print row
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


	print "---------------Processing-------------"

	# df_nr = df[df['status']=='Needs Reply']

	status_priority = [1,2]

	def filter_prior(x):
		if x == 'Needs Reply':
			return status_priority[0]
		else:
			return status_priority[1]

	if debug:
		print "Assigning priority"

	df_nr = df.copy()
	df_nr['status'] = df_nr['status'].apply(filter_prior)

	#Ticket Assigning priority setting

	if debug:
		print "Priority assignment complete"

	if debug:
		print "Arranging according to priority"

	df_nr.sort_values(priority_setting[0])
	
	if priority_setting[0] == 'status':
		level1_val = status_priority
	else:
		level1_val = ['Sev 4','Sev 3','Sev 2','Sev 1']

	temp_df = pd.DataFrame([], columns=df_nr.columns)

	for x in level1_val:
		temp_df = temp_df.append(df_nr[df_nr[priority_setting[0]] == x].sort_values(priority_setting[1]))

	# df_nr_severity = df_nr.sort_values('status')
	
	# if debug:
	# 	print temp_df[['status','severity','ticket_number']]

	df_nr_severity = temp_df	

	skills_tracker = skills_tracker.sort_values('LEVEL')
	# print skills_tracker

	if debug:
		print "Sort by priority complete"

	all_ticket_no = pd.unique(df['ticket_number'])
	total_tickets = len(all_ticket_no)
	number_of_assigned = 0

	pattern = re.compile(r'.*\[S-MAP-IN\] (.*)')
	# for index,row in df_nr.iterrows():
	for t_no in all_ticket_no:

		print "Assigning ",t_no

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
			print "ticket number: ",row['ticket_number']

		if csr_person != None:
			employee = csr_person.group(1)
			employee = clean_name_index(employee)
			#Assign to person set assigned to True
			
			try:
				availability = employee_status[employee]['total_availability'] - employee_status[employee]['usage']
				if availability >= category_time_requirements[ticket_category]:
					if debug:
						print "assigned directly to ",employee
					employee_status[employee]['tickets'].append(row['ticket_number'])
					employee_status[employee]['usage']+=category_time_requirements[ticket_category]
					assigned = True
				# print employee_status[employee]

			except KeyError:
				if debug:
					print "WARNING: No data found for ",employee,". Reassigning ticket"

		maxdtime = 0

		if not assigned:
			#Assign to particular csr based on availability and ticket history
			employee = ''
			temp_df = pd.DataFrame(couch_handle.document_by_key('ticket_number',row['ticket_number']))
			for index1,row1 in temp_df.iterrows():
				# if row1['action_date'][:10]==date_param:
				# 	break

				temp_dtime = datetime.datetime.strptime(row1['action_date'],ticket_dtime_format)

				pre_max = False

				if temp_dtime == ticket_dtime:
					break
				elif maxdtime == 0:
					maxdtime = temp_dtime
					pre_max = True
				elif temp_dtime > maxdtime:
					maxdtime = temp_dtime
					pre_max = True

				if pre_max:
					csr_person = re.search(pattern,row1['performed_by_csr'])
					if csr_person!=None:
						employee = csr_person.group(1)
			
			try:
				availability = employee_status[employee]['total_availability'] - employee_status[employee]['usage']
				if availability >= category_time_requirements[ticket_category]:
					if debug:
						print "assigned from history to ",employee
					employee_status[employee]['tickets'].append(row['ticket_number'])
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
			# print temp_skills

			for i,r in temp_skills.iterrows():
				employee = r['NAME']
				try:
					availability = employee_status[employee]['total_availability'] - employee_status[employee]['usage']
					# print availability
					
					if availability >= category_time_requirements[ticket_category]:
						if debug:
							print "assigned using scheduler to ",employee
						employee_status[employee]['tickets'].append(row['ticket_number'])
						employee_status[employee]['usage']+=category_time_requirements[ticket_category]
						assigned = True
						break

				except KeyError:
					print "WARNING: No data found for ",employee,". Reassigning ticket"
					pass
		
		if not assigned:
			if debug:
				print "Unable to assign ticket"
		else:
			number_of_assigned += 1
			completed_tickets.append(row['ticket_number'])

	# print completed_tickets

	print "Setting completed tickets as assigned"
	couch_handle.set_assigned(completed_tickets,'triager_tickets')
	print "Setting assigned complete"

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
				print "\t",x

	for x in employee_status:
		if employee_status[x]['total_availability'] > 0:
			available_employees+=1

	print "-----------------System Status-------------------"
	print "Total tickets: ",total_tickets
	print "Tickets assigned: ",number_of_assigned
	print "Total employees: ",len(employee_status)
	print "Employees available: ",available_employees
	print "%f assigned: ",((1.0*number_of_assigned/total_tickets)*100),"%"

	if available_employees == 0 or number_of_assigned == 0:
		return [ False, employee_status ]

	if total_tickets != 0 and number_of_assigned !=0 and  total_tickets != number_of_assigned:
		return [ False, employee_status ]
	else:
		return [ True, employee_status ]

	# print employee_status