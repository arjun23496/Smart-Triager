from flask import Flask, request, jsonify
from flask import render_template
from flask_socketio import SocketIO, emit, disconnect
import execute_scheduler
import numpy
import os
import gevent

#API imports
import api.uploader as uploader

socket_app = Flask(__name__)	#socket_server initialization
app = Flask(__name__,template_folder="app/template", static_folder="app/static")  # still relative to module

#Server Configurations
# app.config['TEMPLATE_FOLDER'] = 'app/template'
# app.config['STATIC_FOLDER'] = 'app/static'
app.config['UPLOAD_FOLDER'] = "triager/data/"
app.config['ALLOWED_EXTENSIONS'] = set(['csv'])

#Socket_App Configurations
socket_app.config['SECRET_KEY'] = 'secret'

#Global Initializations
socketio = SocketIO(socket_app)
date = "6 June, 2017"

"""
The index page"(Server Functions)
"""
@app.route('/')
def get_game():
	return render_template("index.html")


@app.route("/scheduler", methods=["GET"])
def scheduler():
	return render_template("execute_scheduler.html")

"""
REST APIS
"""
@app.route("/upload", methods=["POST"])
def uploader_api():

	response_object = {
		'status': 200,
		'data': ''
	}

	global date
	date = request.form['date']

	if date == None or date == "":
		response_object['status'] = 500
		response_object['data'] = "Invalid date"
		return jsonify(response_object)

	res = uploader.upload(app,request,response_object)
	return res


@app.route("/scheduler/getstatus", methods=["POST"])
def get_status():
	print "Initialising socket"

	socketio.run(socket_app, port=5001)
	return "Socket Complete"

#Socket app endpoints
@socketio.on('connect')
def test_connect():
    print "connected"
    return True


@socketio.on('start_scheduler')
def start_scheduler(data):
	emit('status_update',"Scheduler Execution Started")
	gevent.sleep(0)
	execute_scheduler.execute()
	disconnect()
	return True


app.run(debug=True, use_reloader=False)