from preprocessor import Tickets
# from utility import WatsonInterface
from utility.CouchInterface import CouchInterface
from sklearn.externals import joblib

import category_learner
import severity_learner
import progressbar
import transformations
import scheduler
import time
import sys
import traceback
import datetime

def inc_date(date_now, ctr):
	ticket_dtime_format = "%Y-%m-%d-%H.%M.%S"
	date_param = date_now['year']+"-"+date_now['month']+"-"+date_now['date']+"-00.00.00"

	date_now = datetime.datetime.strptime(date_param, ticket_dtime_format)

	date_now = date_now+datetime.timedelta(days=ctr)

	ret = {
			"year": str(date_now.year),
			"month": str(date_now.month),
			"date": str(date_now.day)
	}

	return ret

######################################## preprocessor testing script

# tkt = Tickets()

# print "uploading xlsx file"
# tkt.upload_tickets_xlsx()

# print "uploading csv tickets"
# tkt.upload_tickets_csv()

######################################## category learner testing
# predictors = category_learner.trainer(restrict_prediction=True, restricted_categories=['S - PER - New Map', 'S - Map Research', 'S - Map Change', 'S - PER - Map Change'])

# joblib.dump(predictors[0], 'predictors/category/transformer.pkl')
# joblib.dump(predictors[1], 'predictors/category/learner.pkl')

######################################## severity learner testing
# predictors = severity_learner.trainer('severity',restrict_prediction=False) #test severity

# joblib.dump(predictors[0], 'predictors/severity/transformer.pkl')
# joblib.dump(predictors[1], 'predictors/severity/learner.pkl')

#text emotion extractor

# corpus = '''Hi Mapping Team,
 
# The issue still persists with the Qty value. 
# Currently in ASN data we are sending SN102 value for all lines as 60 it should be 5.Could you tell me in this scenario from where SN102 value is populating? 
 
# Attached the file from Production for testing. Attached the current output and expected output(Comment(29)). 
 
# Note: Please assign the ticket to Dipayan if possible. 
 
# Thanks, 
# Madhu'''

# WatsonInterface.analyse_text_tone_analyser(corpus)

# couchi = CouchInterface()
# dataf = pd.DataFrame(couchi.get_all_documents('triager_tickets'))

######################################### Transformer testing

couch_handle = CouchInterface()

try:
	print "Creating temporary database..."
	couch_handle.create_database()
except Exception:
	print "Retrying..."
	couch_handle.cleanup('triager_tickets')
	couch_handle.create_database()

tkt = Tickets()

print "uploading csv tickets"
tkt.upload_tickets_csv()

date_now = {
		"year": "2017",
		"date": "27",
		"month": "04"
	}

start_time = time.time()

ret = False

employee_status = {}

while not ret:
	try:
		print "Scheduling for ",date_now
		ret = scheduler.execute(date_now)
		
		if employee_status == {}:
			employee_status = ret[1].copy()
		
		ticket_assignment = {}
		ticket_assignment['date'] = date_now
		ticket_assignment['ticket_list'] = []
		ticket_assignment['usage'] = 0
		ticket_assignment['availability'] = 0
		for x in ret[1]:
			ticket_assignment['ticket_list'] = ret[1][x]['tickets']
			ticket_assignment['usage'] = ret[1][x]['usage']
			ticket_assignment['availability'] = ret[1][x]['total_availability']
			try:
				employee_status[x]['daily_assignment']
			except KeyError:
				employee_status[x]['daily_assignment'] = []
			employee_status[x]['daily_assignment'].append(ticket_assignment.copy())

		ret = ret[0]

		date_now = inc_date(date_now,1)
	except:
		exc_type, exc_value, exc_traceback = sys.exc_info()	
		print "Scheduling Terminated"
		traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
		ret = True

elapsed = time.time() - start_time

print employee_status

print "Execution Time: ",elapsed," seconds"

print "Cleaning up database..."
couch_handle.cleanup('triager_tickets')

print "*** Execution Complete ***"