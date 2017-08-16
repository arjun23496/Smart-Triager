var socket = io.connect('http://' + document.domain + ':5001');;

function output(x, mode=1){
	x = x.replace(/\n/g,'<br>')
	console.log(x)
	if(mode==1){
		$('#output-div').append("<code>"+x+"</code><br>");
	}
	if(mode==2){
		$('#output-div').append("<code style='color: red;'>"+x+"</code><br>");	
	}
	if(mode==3){
		$('#output-div').append("<code style='color: #1976D2;'>"+x+"</code><br>");
	}
}

function autoscroll(){
	$('#output-div').scrollTop(document.getElementById('output-div').scrollHeight)
}

socket.on('connect', function() {
	output('Connected',mode=3)
	autoscroll()    	
	socket.emit('ack')
	$('#main-progress').hide()
	return true;
});


socket.on('system_status', function(data){
	output("System: "+data, mode=3)
	if(data=="scheduler_start")
	{
		$('#main-progress').show()
	}

	if(data=="scheduler_running")
	{
		Materialize.toast('Scheduler already running', 8000)
	}

	if(data=="scheduler_error_end")
	{
		$('#status-box').text('Scheduler Terminated with errors')
		$('#main-progress').hide()
	}

	if(data=="scheduler_end")
	{
		$('#status-box').text('Execution Complete')
		$('#main-progress').hide()
		$('#continue').removeClass('disabled')
	}
	autoscroll()
	return false
});


socket.on('status_update', function(data){
	
	$('#status-box').text('Executing Scheduler')

	output(data);
	socket.emit('ack');
	autoscroll()
	return false;
});

socket.on('error', function(data){
	output(data, mode=2)
});

socket.on('status_progress', function(data){
	console.log(data)
	
	$('#status-box').text('Executing Scheduler')
	$('#main-progress').show()

	$('#determinate-progress-wrapper').show()
	var perc = (data['index']+data['step'])*100/data['max']
	if(perc>100)
		perc=100
	
	perc = Math.ceil(perc).toString()


	$('#determinate-status-box').text(data['message']+" ("+perc+"%)")

	$('#determinate-progress').css('width',perc+"%")

	return false
});


socket.on('disconnect', function() {
	output('Connection Closed', mode="2")
	$('#start_scheduler').removeClass('disabled');
	$('#status-box').text('Execution Complete')
	$('#main-progress').hide()
	autoscroll()
	return false;
});

$(document).ready(function(){

	$('#start_scheduler').click(function(){
		socket.emit('start_scheduler')
		$('#status-box').text('Executing Scheduler')
	});

	$("#status-box").text('Initailization Complete');

	$('#main-progress').hide()

	$('#start_scheduler').removeClass('disabled');

	$('#determinate-progress-wrapper').hide();
});