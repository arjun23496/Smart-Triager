var triager_report;
var ticket_report;
var employee_report;

function sanitize_json(x)
{
	x = x.replace(/u/g,'')
	x = x.replace(/'/g,'"')
	x = JSON.parse(x)

	return x	
}

$(document).ready(function(){
	triager_report = $('#triager-report').data()
	ticket_report = $('#ticket-report').data()
	employee_report = $('#employee-report').data()
	
	triager_report = sanitize_json(triager_report["name"])
	console.log("triager_report sanitized")
	console.log(ticket_report)
	ticket_report = sanitize_json(ticket_report['name'])
	console.log("ticket report sanitized")
	employee_report = sanitize_json(employee_report['name'])
	console.log("triager_report sanitized")

	console.log(triager_report)
	console.log(ticket_report)
	console.log(employee_report)

	$('#report_date').text(triager_report['date'])
	$('#n_new_map').text(triager_report['category_report']['New Map'])
	$('#n_map_change').text(triager_report['category_report']['PER Map Change'])
	$('#n_change').text(triager_report['category_report']['Change'])
	$('#n_research').text(triager_report['category_report']['Research'])
	$('#n_priority').text(triager_report['priority_deliverables'])
	$('#n_members').text(triager_report['available_members'])

	$('#main-progress').hide()
});