function update_file_list(file_list)
{
	var thtml = '<div class="collection-header"><h4>Data Folder</h4></div>'
	thtml+='<div class="collection-item"><b>NAME</b><span class="right"><b>DATE MODIFIED</b></span></div>'
	
	var add_status = false
	var missing_status = false
	for(x in file_list)
	{
		if(file_list[x]!="")
		{
			add_status=true
			thtml+='<a class="collection-item">'+x+'<span class="right">'+file_list[x]+'</span></a>'
		}
		else{
			missing_status = true
		}
	}

	if(!add_status)
		thtml += '<div class="collection-item">No Files Found</div>'

	if(!missing_status)
		$('#continue').removeClass('disabled')

	$('#file_list_display').html(thtml);
}


function notify(mesg){
	mesg = mesg.split(';')
	for(x in mesg)
	{
		Materialize.toast(mesg[x], 8000)
	}
}


$('form#upload_documents').submit(function(){
	console.log("submit")
	var formData = new FormData(this);
	$('#upload_progress').show();
	$.ajax({
		url: '/upload',
		type: 'POST',
		data: formData,
		success: function(data){
			// console.log("success")
			// console.log(data)
			// console.log(data['data'])
			notify(data['data'])
			$('#upload_progress').hide();

			console.log(data['status'])
			if(data['status'] == "200"){
				// $('#upload_files').addClass('disabled');
				$('#continue').removeClass('disabled');
			}
			if(data['status'] == "500"){
				notify('Multiple Files Missing. Unable to Continue')
			}

			update_file_list(data['file_list'])
		},
		error: function(data){
			Materialize.toast('Server Error',8000);
			$('#upload_progress').hide();	
		},
		cache: false,
		contentType: false,
		processData: false
	});

	return false
});


$(document).ready(function(){
	
	startup()
	get_scheduler_status()
	listen_scheduler_status()
	
	$('.datepicker').pickadate({
	    selectMonths: true, // Creates a dropdown to control month
	    selectYears: 15, // Creates a dropdown of 15 years to control year,
	    today: 'Today',
	    clear: 'Clear',
	    close: 'Ok',
	    closeOnSelect: false // Close upon selecting a date,
	  });

	file_list = $('#file_list').data()
	file_list = sanitize_json(file_list['name'])

	update_file_list(file_list)
	
	$('#upload_progress').hide()
});