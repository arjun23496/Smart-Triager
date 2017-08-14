var socket = io.connect('http://' + document.domain + ':5001');;

function output(x, mode=1){
	if(mode==1){
		console.log(x)
		$('#output-div').append("<code>"+x+"</code><br>");
	}
}

function autoscroll(){
	$('#output-div').scrollTop(document.getElementById('output-div').scrollHeight)
}

socket.on('connect', function() {
	output('Connected')
	autoscroll()    	
	socket.emit('ack')
	$('#main-progress').hide()
	return true;
});


socket.on('system_status', function(data){
	output("System: "+data)
	if(data=="thread_complete")
	{
		socket.emit('thread_complete')
	}
	autoscroll()
	return false
});


socket.on('status_update', function(data){
	
	$('#status-box').text('Executing Scheduler')
	$('#main-progress').show()

	output(data);
	socket.emit('ack');
	autoscroll()
	return false;
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
	output('Connection Closed')
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
		$('#main-progress').show()
	});

	$("#status-box").text('Initailization Complete');

	$('#start_scheduler').removeClass('disabled');

	$('#determinate-progress-wrapper').hide();
});