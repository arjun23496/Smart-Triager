import couchdb
import json
import progressbar


class CouchInterface:

	def __init__(self,address='http://admin:arjun23496@localhost:5984/'):
		try:
			self.handle = couchdb.Server(address)
		except Exception:
			print "!!!!!! Connection to database Failed !!!!!!"

	def add_documents(self, dbname, document):
		try:
			db = self.handle[dbname]
		except Exception:
			print "!!!!!! Database "+dbname+" not detected !!!!!!"

		print "Uploading "+str(len(document))+" document(s).."

		bar = progressbar.ProgressBar(maxval=len(document), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
		success = 0

		bar.start()
		for x in range(0,len(document)):
			# doc = json.dumps(document[x])
			# doc = json.loads(doc)

			try:
				# doc_id, doc_rev = db.save(doc)
				document[x].store(db)
				success=success+1
			except Exception as detail:
				print detail
				print "document index "+str(x)+" failed"
				return success

			bar.update(x+1)
		
		bar.finish()

		return success


	def document_by_key(self, key, value, dbname):
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


	def get_all_documents(self, dbname):
		db = self.handle[dbname]
		
		map_fun = '''function (doc){			
			emit(doc,null);
		}'''

		return_value = []

		for row in db.query(map_fun):
			return_value.append(row.key)

		return return_value