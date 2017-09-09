from preprocessor import Tickets
# from utility import WatsonInterface
from utility.CouchInterface import CouchInterface
from utility.custom_output import CustomOutput
from sklearn.externals import joblib

import category_learner
import severity_learner
import progressbar
import transformations
import scheduler
import time
import traceback

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

coutput = CustomOutput()
tkt.upload_tickets_csv(coutput=coutput, output_mode=1)

date_now = {
		"year": "2017",
		"date": "20",
		"month": "07"
	}

start_time = time.time()

try:
	scheduler.execute(date_now, output_mode=1)
except Exception as e:
	print "Scheduling Terminated"
	traceback.format_exc()

elapsed = time.time() - start_time

print "Execution Time: ",elapsed," seconds"

print "Cleaning up database..."
couch_handle.cleanup('triager_tickets')

print "*** Execution Complete ***"