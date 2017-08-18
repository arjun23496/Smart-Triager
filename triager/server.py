from flask import Flask, request, jsonify, send_file
from flask import render_template
from flask_socketio import SocketIO, emit, disconnect
import numpy
import os
import json
import datetime

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


def get_files():
	file_list = {
		"scheduler_date.json": "",
		"ticket_list.csv": "",
		"vacation_plan.csv": "",
		"skills_tracker.csv": "",
		"backlog.csv": ""
	}

	for key in file_list:
		path = os.path.join(app.config['UPLOAD_FOLDER'], key)
		if os.path.isfile(path):
			file_list[key] = datetime.datetime.fromtimestamp(int(os.path.getmtime(path))).strftime('%Y-%m-%d %H:%M:%S')

	return file_list


"""
The index page"(Server Functions)
"""
@app.route('/')
@app.route('/upload', methods=["GET"])
def get_index():
	# try:
	# 	with open(os.path.join(os.path.dirname(__file__),'report/triager_summary_report.json'), 'rb') as fp:
	# 		date = json.load(fp)
	# 		date = date['date']
	# except IOError:
	# 	date = ""
	file_list = get_files()
	print file_list
	return render_template("index.html", file_list=file_list)


@app.route("/scheduler", methods=["GET"])
def scheduler():
	# try:
	# 	with open(os.path.join(os.path.dirname(__file__),'report/triager_summary_report.json'), 'rb') as fp:
	# 		date = json.load(fp)
	# 		date = date['date']
	# except IOError:
	# 	date = ""
	return render_template("execute_scheduler.html")


@app.route("/report", methods=["GET"])
def reporter():
	date = ""
	triager_report = {}
	ticket_report = {}
	employee_report = {}
	
	try:
		with open(os.path.join(os.path.dirname(__file__),'report/triager_summary_report.json'), 'rb') as fp:
			triager_report = json.load(fp)

		with open(os.path.join(os.path.dirname(__file__),'report/ticket_report.json'), 'rb') as fp:
			ticket_report = json.load(fp)

		with open(os.path.join(os.path.dirname(__file__),'report/employee_status_report.json'), 'rb') as fp:
			employee_report = json.load(fp)
	except IOError:
		pass

	print triager_report

	return render_template("report.html", triager_report=triager_report, ticket_report=ticket_report, employee_report=employee_report)


@app.route("/get_excel_report", methods=["GET"])
def get_excel_file():
	path = os.path.join(os.path.dirname(__file__),'report/report.xlsx')
	
	if os.path.isfile(path):
		with open(os.path.join(os.path.dirname(__file__),'report/triager_summary_report.json'), 'rb') as fp:
			date = json.load(fp)
			date = date['date']
		return send_file(path, as_attachment=True, attachment_filename="Triager_Report - "+date+".xlsx")
	else:
		return "Report not found"
"""
REST APIS
"""

@app.route("/get_scheduler_status", methods=["POST"])
def get_scheduler_status():
	scheduler_status = ''
	with open(os.path.join(os.path.dirname(__file__),'scheduler_status.json'), 'rb') as fp:
		scheduler_status = json.load(fp)
	try:
		with open(os.path.join(os.path.dirname(__file__),'report/triager_summary_report.json'), 'rb') as fp:
			date = json.load(fp)
			scheduler_status['date'] = date['date']
	except IOError:
		scheduler_status['date'] = ""

	return jsonify(scheduler_status)


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
		'data': '',
		'file_list': {}
	}

	global date
	date = request.form['date']

	if date == None or date == "":
		# response_object['status'] = 500
		if not os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], "scheduler_date.json")):
			response_object['status'] = 500
			response_object['data'] = "Date not detected"
		else:
			response_object['data'] = "Date not Uploaded. Using existing..."
		# return jsonify(response_object)
	else:
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

		try:
			with open(os.path.join(os.path.dirname(__file__),'data/scheduler_date.json'), 'w') as fp:
				json.dump(date_sav, fp)
			response_object['data'] = "Date Uploaded"
		except IOError:
			response_object['status'] = 500
			response_object['data'] += ";Error Uploading Date"

	res = uploader.upload(app,request,response_object)
	
	res['file_list'] = get_files()

	print res
	return jsonify(res)

app.run(debug=True, use_reloader=False, host="0.0.0.0", threaded=True)