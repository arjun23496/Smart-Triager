from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, disconnect
from threading import Lock
from preprocessor import Tickets
from utility.CouchInterface import CouchInterface
from utility.custom_output import CustomOutput
from utility.custom_output import cprint

import gevent
import execute_scheduler
import time
import scheduler
import json
import os

socket_app = Flask(__name__)	#socket_server initialization

#Socket server configurations
socket_app.config['SECRET_KEY'] = 'secret'

# socketio = SocketIO(socket_app, engineio_logger=True, threaded=True, ping_timeout=600)
socketio = SocketIO(socket_app, threaded=True, ping_timeout=600)
thread_lock = Lock()

scheduler_status = False


def execute():
	coutput = CustomOutput(thread=True, socketio=socketio);
	couch_handle = CouchInterface(output_interface=coutput);

	cprint("Creating temporary database...", "status_update", mode=2, socketio=socketio, thread=True)

	try:
		couch_handle.create_database()
	except Exception:
		cprint("Retrying...", "status_update", mode=2, socketio=socketio, thread=True)
		couch_handle.cleanup('triager_tickets')
		couch_handle.create_database()

	cprint("Temporary database created", "status_update", mode=2, socketio=socketio, thread=True)

	tkt = Tickets()

	cprint("Uploading csv tickets", "status_update", mode=2, socketio=socketio, thread=True)
	tkt.upload_tickets_csv(coutput=coutput)

	with open(os.path.join(os.path.dirname(__file__),'data/scheduler_date.json'), 'rb') as fp:
		date_now = json.load(fp)
	
	start_time = time.time()

	try:
		scheduler.execute(date_now, thread=True, socketio=socketio)
	except Exception as e:
		cprint("Scheduling teminated", "error", mode=2, socketio=socketio, thread=True)
		print e
		cprint(str(e), "error", mode=2, socketio=socketio, thread=True)
	
	elapsed = time.time() - start_time
	coutput.cprint("Execution Time: "+str(elapsed)+" seconds", "status_update", mode=2)
	
	coutput.cprint("Cleaning up database...", "status_update", mode=2)
	couch_handle.cleanup('triager_tickets')

	coutput.cprint("*** Execution Complete ***", "status_update", mode=2)
	coutput.cprint('scheduler_end','system_status',mode=2)



#Socket app endpoints
@socketio.on('connect')
def test_connect():
    print "connected"
    cprint("connected", "system_status", mode=2)


@socketio.on('disconnect')
def test_disconnect():
    print "disconnected"
    cprint("Disconnected", "system_status", mode=2)


@socketio.on('get_status')
def get_connection_status():
	cprint("live", "system_status", mode=2)


@socketio.on('start_scheduler')
def start_scheduler():

	global scheduler_status

	if not scheduler_status:
		cprint("scheduler_start", "system_status", mode=2)
		print "Scheduler Started"
		scheduler_status=True

		# execute_scheduler.execute()
		thread = socketio.start_background_task(target=execute)
		
		# 	sthread.start()

		scheduler_status=False
		cprint("Scheduler Execution Complete", "system_status", mode=2)
	else:
		print "Scheduler already running"
		cprint("Scheduler Already Running...", "system_status", mode=2)


@socketio.on('system_status')
def thread_complete(data):
	if data=="thread_complete":
		global scheduler_status
		scheduler_status=False


@socketio.on('ack')
def acknowledge():
	# print "ack"
	pass


socketio.run(socket_app, debug=True, port=5001);