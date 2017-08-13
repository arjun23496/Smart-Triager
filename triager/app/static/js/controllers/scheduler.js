var socket = io.connect('http://' + document.domain + ':5001');;

function output(x, mode=1){
	if(mode==1){
		console.log(x)
		$('#output-div').append("<code>"+x+"</code><br>");
	}
}

socket.on('connect', function() {
	output('Connected')    	
	socket.emit('ack')
	return true;
});


socket.on('system_status', function(data){
	output("System: "+data)
	if(data=="thread_complete")
	{
		socket.emit('thread_complete')
	}
	return false
});


socket.on('status_update', function(data){
	output(data);
	socket.emit('ack');
	return false;
});


socket.on('status_progress', function(data){
	console.log(data)
	socket.emit('ack');
	return false
});


socket.on('disconnect', function() {
	output('Connection Closed')
	$('#start_scheduler').removeClass('disabled');
	return false;
});

$(document).ready(function(){

	$('#start_scheduler').click(function(){
		socket.emit('start_scheduler')	
	});

	$("#status-box").text('Initailization Complete');

	$('#start_scheduler').removeClass('disabled');

});