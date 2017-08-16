from flask import jsonify
import os

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in set(['csv'])


def upload(app, request, response_object):

	file = request.files['ticket_list']
	
	path = os.path.join(app.config['UPLOAD_FOLDER'], "ticket_list.csv")
	if file and allowed_file(file.filename):
		file.save(path)
		os.chmod(path,0775)
		response_object['data'] += ';Ticket List Uploaded'
	else:
		if not os.path.isfile(path):
			response_object['status'] = 500
			response_object['data'] += ';Error in Ticket List file'
		else:
			response_object['data'] += ';Ticket List Not Uploaded. Using existing...'
		
	file = request.files['skills_tracker']
	if file and allowed_file(file.filename):
		path = os.path.join(app.config['UPLOAD_FOLDER'], "skills_tracker.csv")
		file.save(path)
		os.chmod(path,0775)
		response_object['data'] += ';Skills Tracker Uploaded'
	else:
		if not os.path.isfile(path):
			response_object['status'] = 500
			response_object['data'] += ';Error in skills tracker file'
		else:
			response_object['data'] += ';Skills Tracker Not Uploaded. Using existing...'
		
	file = request.files['vacation_planner']
	if file and allowed_file(file.filename):
		path = os.path.join(app.config['UPLOAD_FOLDER'], "vacation_plan.csv")
		file.save(path)
		os.chmod(path,0775)
		response_object['data'] += ';Vacation Plan Uploaded'
	else:
		if not os.path.isfile(path):
			response_object['status'] = 500
			response_object['data'] += ';Error in Vacation Planner file'
		else:
			response_object['data'] += ';Vacation Planner Not Uploaded. Using existing...'
		
	file = request.files['backlog']
	if file and allowed_file(file.filename):
		path = os.path.join(app.config['UPLOAD_FOLDER'], "backlog.csv")
		file.save(path)
		os.chmod(path,0775)
		response_object['data'] += ';Backlog Uploaded'
	else:
		if not os.path.isfile(path):
			response_object['status'] = 500
			response_object['data'] += ';Error in Backlog/Pending Cases file'
		else:
			response_object['data'] += ';Backlog Not Uploaded. Using existing...'

	return response_object