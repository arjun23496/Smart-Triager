$(document).ready(function(){
	$('#upload_progress').hide()
	
	$('.datepicker').pickadate({
	    selectMonths: true, // Creates a dropdown to control month
	    selectYears: 15, // Creates a dropdown of 15 years to control year,
	    today: 'Today',
	    clear: 'Clear',
	    close: 'Ok',
	    closeOnSelect: false // Close upon selecting a date,
	  });

});


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
			Materialize.toast(data['data'],8000);
			$('#upload_progress').hide();

			console.log(data['status'])
			if(data['status'] == "200"){
				$('#upload_files').addClass('disabled');
				$('#continue').removeClass('disabled');
			}
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