from flask import jsonify
import os

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in set(['csv'])


def upload(app,request,response_object):

	file = request.files['ticket_list']
	if file and allowed_file(file.filename):
		path = os.path.join(app.config['UPLOAD_FOLDER'], "ticket_list.csv")
		file.save(path)
		os.chmod(path,0775)
	else:
		response_object['status'] = 500
		response_object['data'] = 'Error in Ticket List file'
		return jsonify(response_object)

	file = request.files['skills_tracker']
	if file and allowed_file(file.filename):
		path = os.path.join(app.config['UPLOAD_FOLDER'], "skills_tracker.csv")
		file.save(path)
		os.chmod(path,0775)
	else:
		response_object['status'] = 500
		response_object['data'] = 'Error in skills tracker file'
		return jsonify(response_object)

	file = request.files['vacation_planner']
	if file and allowed_file(file.filename):
		path = os.path.join(app.config['UPLOAD_FOLDER'], "vacation_plan.csv")
		file.save(path)
		os.chmod(path,0775)
	else:
		response_object['status'] = 500
		response_object['data'] = 'Error in Vacation Planner file'
		return jsonify(response_object)

	file = request.files['backlog']
	if file and allowed_file(file.filename):
		path = os.path.join(app.config['UPLOAD_FOLDER'], "backlog.csv")
		file.save(path)
		os.chmod(path,0775)
	else:
		response_object['status'] = 500
		response_object['data'] = 'Error in Backlog/Pending Cases file'
		return jsonify(response_object)

	response_object['status'] = 200
	response_object['data'] = 'Upload succesfully Completed'

	return jsonify(response_object)