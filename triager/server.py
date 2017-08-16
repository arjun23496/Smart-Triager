from flask import Flask, request, jsonify
from flask import render_template
from flask_socketio import SocketIO, emit, disconnect
import numpy
import os
import json

#API imports
import api.uploader as uploader

app = Flask(__name__,template_folder="app/template", static_folder="app/static")  # still relative to module

#Server Configurations
# app.config['TEMPLATE_FOLDER'] = 'app/template'
# app.config['STATIC_FOLDER'] = 'app/static'
app.config['UPLOAD_FOLDER'] = "data/"
app.config['ALLOWED_EXTENSIONS'] = set(['csv'])

#Global Initializations
date = "6 June, 2017"

"""
The index page"(Server Functions)
"""
@app.route('/')
@app.route('/upload', methods=["GET"])
def get_index():
	try:
		with open(os.path.join(os.path.dirname(__file__),'report/triager_summary_report.json'), 'rb') as fp:
			date = json.load(fp)
			date = date['date']
	except IOError:
		date = ""
	return render_template("index.html", date=date)


@app.route("/scheduler", methods=["GET"])
def scheduler():
	try:
		with open(os.path.join(os.path.dirname(__file__),'report/triager_summary_report.json'), 'rb') as fp:
			date = json.load(fp)
			date = date['date']
	except IOError:
		date = ""
	return render_template("execute_scheduler.html", date=date)


@app.route("/report", methods=["GET"])
def reporter():
	date = ""
	triager_report = {}
	ticket_report = {}
	employee_report = {}
	
	try:
		with open(os.path.join(os.path.dirname(__file__),'report/triager_summary_report.json'), 'rb') as fp:
			triager_report = json.load(fp)
			date = triager_report['date']

		with open(os.path.join(os.path.dirname(__file__),'report/ticket_report.json'), 'rb') as fp:
			ticket_report = json.load(fp)

		with open(os.path.join(os.path.dirname(__file__),'report/employee_status_report.json'), 'rb') as fp:
			employee_report = json.load(fp)
	except IOError:
		pass

	print triager_report

	return render_template("report.html", date=date, triager_report=triager_report, ticket_report=ticket_report, employee_report=employee_report)

"""
REST APIS
"""
@app.route("/upload", methods=["POST"])
def uploader_api():

	month_map = {
		"January,": u"01",
		"February,": u"02",
		"March,":	u"03",
		"April,":	u"04",
		"May,":		u"05",
		"June,":		u"06",
		"July,":		u"07",
		"August,":	u"08",
		"September,":u"09",
		"October,":	u"10",
		"November,":	u"11",
		"December,":	u"12"
	}

	response_object = {
		'status': 200,
		'data': ''
	}

	global date
	date = request.form['date']

	if date == None or date == "":
		return jsonify(response_object)

	date = date.split(" ");
	if len(date[0]) == 1:
		date[0] = "0"+date[0]

	date[1] = month_map[date[1]]

	print date

	date_sav = {
		"year": date[2],
		"date": date[0],
		"month": date[1]
	}

	with open(os.path.join(os.path.dirname(__file__),'data/scheduler_date.json'), 'w') as fp:
		json.dump(date_sav, fp)

	response_object['status'] = 500
	response_object['data'] = "Invalid date"

	res = uploader.upload(app,request,response_object)
	return res

app.run(debug=True, use_reloader=False)