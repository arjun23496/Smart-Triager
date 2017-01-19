from datetime import datetime
from couchdb.mapping import Document, TextField, IntegerField, DateTimeField

class Ticket(Document):
	ticket_number = TextField()
	account_name = TextField()
	severity = TextField()
	service_offering = TextField()
	action = TextField()
	action_past_tense = TextField()
	action_date = DateTimeField(default=datetime.now)
	status = TextField()
	assigned_to_csr = TextField()
	performed_by_csr = TextField()
	new_queue = TextField()
	category = TextField()
	comments = TextField()
	summary = TextField()
	additional_info_1 = TextField()
	additional_info_2 = TextField()
	alert_indicator = TextField()
	alert_comments = TextField()
	detail = TextField()