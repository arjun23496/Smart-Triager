from HTMLParser import HTMLParser
import couchdb
import json


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

class CouchInterface:

	def __init__(self,address='http://localhost:5984/'):
		self.handle = couchdb.Server(address)

	def add_documents(self, dbname, document):
		db = self.handle[dbname]
		
		import progressbar

		bar = progressbar.ProgressBar(maxval=len(document), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
		# for i in xrange(20):
		#     bar.update(i+1)
		#     sleep(0.1)
		# bar.finish()


		bar.start()
		for x in range(0,len(document)):
			doc = json.dumps(document[x])
			doc = json.loads(doc)
			db.save(doc)
			bar.update(x+1)
		
		bar.finish()

		return True