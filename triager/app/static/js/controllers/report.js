var triager_report;
var ticket_report;
var employee_report;

function populate_triage_report(triager_report)
{
	$('#report_date').text(triager_report['date'])
	$('#n_new_map').text(triager_report['category_report']['New Map'])
	$('#n_map_change').text(triager_report['category_report']['PER Map Change'])
	$('#n_change').text(triager_report['category_report']['Change'])
	$('#n_research').text(triager_report['category_report']['Research'])
	$('#n_priority').text(triager_report['priority_deliverables'])
	$('#n_backlog_sev1').text(triager_report['backlog_report']['Sev 1'])
	$('#n_backlog_sev2').text(triager_report['backlog_report']['Sev 2'])
	$('#n_backlog_sev3').text(triager_report['backlog_report']['Sev 3'])
	$('#n_backlog_sev4').text(triager_report['backlog_report']['Sev 4'])
	$('#n_members').text(triager_report['available_members'])
	$('#n_b2b').text(triager_report['new_map_report']['b2b'])
	$('#n_b2bi').text(triager_report['new_map_report']['b2bi'])
	$('#n_allocated').text(triager_report['total_allocated'])
}

function populate_allocation_table(employee_report, ticket_report){
	var tbody = $('#allocation_table_body')
	for(employee in employee_report)
	{
		thtml = ""
		if(employee_report[employee]['tickets'].length > 0)
		{
			console.log(employee_report[employee]['tickets'])
			ticket_list = employee_report[employee]['tickets'].split(';')
			
			thtml = "<tr><td rowspan="+ticket_list.length+"\>"+employee+"</td>"

			var i=0;
			for(ticket in ticket_list)
			{
				x=ticket_list[ticket]
				if(i!=0)
					thtml+="<tr>"
				console.log(ticket_report[x]['backlog'])
				if(ticket_report[x]['backlog'])
				{
					thtml+="<td class='backlog-row'>"+x+"</td>"
					thtml+="<td class='backlog-row'>"+ticket_report[x]['customer']+"</td>"
					thtml+="<td class='backlog-row'>"+ticket_report[x]['severity']+"</td>"
					thtml+="<td class='backlog-row'>"+ticket_report[x]['category']+"</td>"
					thtml+="<td class='backlog-row'>"+ticket_report[x]['status']+"</td>"
					thtml+="<td class='backlog-row' style='text-align: left;'>"+ticket_report[x]['triage_recommendation']+"</td>"
					thtml+="<td class='backlog-row'>"+ticket_report[x]['last_worked_by']+"</td>"
					thtml+="</tr>"
				}
				else
				{
					thtml+="<td>"+x+"</td>"
					thtml+="<td>"+ticket_report[x]['customer']+"</td>"
					thtml+="<td>"+ticket_report[x]['severity']+"</td>"
					thtml+="<td>"+ticket_report[x]['category']+"</td>"
					thtml+="<td>"+ticket_report[x]['status']+"</td>"
					thtml+="<td style='text-align: left;'>"+ticket_report[x]['triage_recommendation']+"</td>"
					thtml+="<td>"+ticket_report[x]['last_worked_by']+"</td>"
					thtml+="</tr>"	
				}
				i+=1;
			}
			thtml+='<tr class="summary_row"><td colspan=8>Total - '+ticket_list.length+' Tickets</td></tr>'
		}

		tbody.append(thtml);
	}
}


$(document).ready(function(){

	get_scheduler_status()
	listen_scheduler_status()

	triager_report = $('#triager-report').data()
	ticket_report = $('#ticket-report').data()
	employee_report = $('#employee-report').data()

	console.log(triager_report)

	if(triager_report=="{}" || ticket_report=="{}" || employee_report=="{}")
	{
		Materialize.toast("No Reports Found","8000")
	}
	else{
		
		triager_report = sanitize_json(triager_report["name"])
		ticket_report = sanitize_json(ticket_report['name'])
		employee_report = sanitize_json(employee_report['name'])

		console.log(triager_report)
		console.log(ticket_report)
		console.log(employee_report)

		populate_triage_report(triager_report)
		$('#triage_summary_table').show()

		populate_allocation_table(employee_report, ticket_report)
		$('#allocation_table').show()	
	}
	
	$('#main-progress').hide()
});