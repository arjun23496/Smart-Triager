from flask_socketio import emit
import gevent

def cprint(val, signal="", mode=1):
	if mode==1:
		print val
	elif mode==2:
		emit(signal, val, broadcast=True)
		gevent.sleep(0)
		print signal," : ",val
	elif mode==3:
		if val['index']%val['step'] == 0 or val['index']==val['max']:
			emit(signal, val, broadcast=True)
			gevent.sleep(0)
		# print signal," : ",val