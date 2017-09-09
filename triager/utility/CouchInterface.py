from custom_output import cprint

import couchdb
import json
import progressbar
import sys

reload(sys)  
sys.setdefaultencoding('utf8')

class CouchInterface:

	def __init__(self,address='http://admin:arjun23496@localhost:5984/', output_interface=None):
		self.coutput = output_interface
		print "self.coutput"
		print self.coutput
		try:
			self.handle = couchdb.Server(address)
		except Exception:
			self.coutput.cprint("!!!!!! Connection to database Failed !!!!!!", "error", mode=2)

	def create_database(self, dbname='triager_tickets'):
		self.handle.create(dbname)

	def add_documents(self, document, dbname='triager_tickets'):
		try:
			db = self.handle[dbname]
		except Exception:
			self.coutput.cprint("!!!!!! Database "+dbname+" not detected !!!!!!", "error", mode=2)

		self.coutput.cprint("Uploading "+str(len(document))+" document(s)..", "status_update", mode=2)

		bar = progressbar.ProgressBar(maxval=len(document), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
		success = 0

		progress_result={
			'message': 'Upload Progress',
			'max': len(document),
			'index': 0,
			'step': 10
		}

		bar.start()
		for x in range(0,len(document)):
			try:
				document[x].store(db)
				success=success+1
			except Exception as detail:
				self.coutput.cprint(str(detail), "error", mode=2)
				self.coutput.cprint("document index "+str(x)+" failed", "error", mode=2)
				return success

			bar.update(x+1)
			progress_result['index'] = x+1
			self.coutput.cprint(progress_result, "status_progress", mode=3)
		
		bar.finish()

		return success


	def document_by_key(self, key, value, dbname="triager_tickets"):
		# try:
		db = self.handle[dbname]
		# except Exception:
		# 	print "!!!!!! Database "+dbname+" not detected !!!!!!"
		# 	return

		map_fun = '''function (doc){
			if(doc.'''+key+''' == \''''+value+'''\')
				emit(doc,null);
		}'''

		return_value = []

		# print db.query(map_fun)
		for row in db.query(map_fun):
			return_value.append(row.key)

		return return_value


	def document_by_assigned(self, key=False, dbname="triager_tickets"):
		# try:
		#2017-01-24
		db = self.handle[dbname]
		# except Exception:
		# 	print "!!!!!! Database "+dbname+" not detected !!!!!!"
		# 	return

		if key:

			# map_fun = '''function (doc){
			# 	if(doc.assigned && doc.action_date.substr(0,4) == "'''+date['year']+'''")
			# 		emit(doc.action_date,doc);
			# }'''
			map_fun = '''function (doc){
				if(doc.assigned)
					emit(doc.action_date,doc);
			}'''
		else:

			# map_fun = '''function (doc){
			# 	if(!doc.assigned && doc.action_date.substr(0,4) == "'''+date['year']+'''" && doc.action_date.substr(5,2) == "'''+date['month']+'''" && doc.action_date.substr(8,2) == "'''+date['date']+'''")
			# 		emit(doc.action_date,doc);
			# }'''
			map_fun = '''function (doc){
				if(!doc.assigned)
					emit(doc.action_date,doc);
			}'''

		return_value = []

		db_return = db.query(map_fun)
		ctr=0
		
		# print db_return.rows

		if len(db_return.rows) > 0:
			print "Retrieving documents from db..."

			bar = progressbar.ProgressBar(maxval=len(db_return), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
			bar.start()

			for row in db_return:
				return_value.append(row.value)
				ctr = ctr+1
				bar.update(ctr)
			
			bar.finish()
		
		return return_value


	def get_all_documents(self, dbname):
		db = self.handle[dbname]
		
		map_fun = '''function (doc){			
			emit(doc,null);
		}'''

		return_value = []

		for row in db.query(map_fun):
			return_value.append(row.key)

		return return_value


	def cleanup(self, dbname='triager_tickets'):
		self.handle.delete(dbname)