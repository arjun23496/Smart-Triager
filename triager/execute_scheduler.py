from preprocessor import Tickets
from utility.CouchInterface import CouchInterface
# from flask_socketio import emit
from sklearn.externals import joblib
from utility.custom_output import cprint

import category_learner
import severity_learner
import progressbar
import transformations
import scheduler
import time
import gevent
import sys

def execute():
	couch_handle = CouchInterface()

	cprint("Creating temporary database...", "status_update", mode=2)

	try:
		couch_handle.create_database()
	except Exception:
		cprint("Retrying...", "status_update", mode=2)
		couch_handle.cleanup('triager_tickets')
		couch_handle.create_database()

	cprint("Temporary database created", "status_update", mode=2)

	tkt = Tickets()

	cprint("Uploading csv tickets", "status_update", mode=2)
	tkt.upload_tickets_csv()

	date_now = {
			"year": "2017",
			"date": "06",
			"month": "06"
		}

	start_time = time.time()

	try:
		scheduler.execute(date_now)
	except Exception as e:
		cprint("Scheduling teminated", "error", mode=2)
		cprint(str(e), "error", mode=2)

	elapsed = time.time() - start_time

	cprint("Execution Time: "+str(elapsed)+" seconds", "status_update", mode=2)

	cprint("Cleaning up database...", "status_update", mode=2)
	couch_handle.cleanup('triager_tickets')

	cprint("*** Execution Complete ***", "status_update", mode=2)