from datetime import datetime
from couchdb.mapping import Document, TextField, IntegerField, DateTimeField, BooleanField

class Ticket(Document):
	ticket_number = TextField()
	account_name = TextField()
	severity = TextField()
	service_offering = TextField()
	action = TextField()
	action_past_tense = TextField()
	action_date = DateTimeField()
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
	assigned = BooleanField(default=False)

csv_mapping = {
	"Ticket Number": "ticket_number",
	"Alert Indicator": "alert_indicator",
	"Alert Comments": "alert_comments",
    "Assigned To (CSR)": "assigned_to_csr",
    "Performed By (CSR)": "performed_by_csr",
    "Account Name": "account_name",
    "Status": "status",
    "Severity": "severity",
    "Service Offering": "service_offering",
    "New Queue": "new_queue",
    "Action": "action",
    "Action Past Tense": "action_past_tense",
    "Action Date": "action_date",
    "Details": "detail",
    "Category": "category",
    "Summary": "summary",
    "Additional Info 1": "additional_info_1",
    "Additional Info 2": "additional_info_2",
    "Comments": "comments"
}