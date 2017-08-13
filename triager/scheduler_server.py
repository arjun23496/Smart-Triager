from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, disconnect
from utility.custom_output import cprint
from scheduler_thread import SchedulerThread
import gevent
import execute_scheduler

socket_app = Flask(__name__)	#socket_server initialization

#Socket server configurations
socket_app.config['SECRET_KEY'] = 'secret'

# socketio = SocketIO(socket_app, engineio_logger=True, threaded=True, ping_timeout=600)
socketio = SocketIO(socket_app, threaded=True, ping_timeout=600)

scheduler_status = False

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
		cprint("Scheduler Execution Started", "system_status", mode=2)
		print "Scheduler Started"
		scheduler_status=True

		execute_scheduler.execute()
		
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