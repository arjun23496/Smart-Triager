from utility import MLStripper
from utility import CouchInterface 

class Tickets:

	def strip_tags(self, html): #helper function to sanitize html tags in comments
	    s = MLStripper()
	    s.feed(html)
	    return s.get_data()

	def upload_tickets(self, file_path="data/Ticket_list.xlsx", worksheet="Tickets in Queue with History"):
		from openpyxl import load_workbook
		
		wb = load_workbook(file_path, read_only=True)
		ws = wb[worksheet]
		rowi = 0
		coli = 0
		template = {}
		template_keys = []
		document = []

		for row in ws.rows:
			rowi = rowi+1
			coli = 0

			if rowi < 2:
				for col in row:
					template[col.value] = ''
					template_keys.append(col.value)
			else:
				for col in row:
					if coli==0 and (col.value==None or col.value==''):
						break
					if template_keys[coli] != 'Action Date':
						if col.value==None:
							val = ''
						else:
							val = col.value
						template[template_keys[coli]] = val
					coli=coli+1

				template['Comments'] = self.strip_tags(template['Comments'])
				template['Alert Comments'] = self.strip_tags(template['Alert Comments'])
				template['Comments'] = template['Comments'].replace('_x000D_',' ')
				template['Alert Comments'] = template['Alert Comments'].replace('_x000D_',' ')
				template['Comments'] = template['Comments'].replace('\n',' ')
				template['Alert Comments'] = template['Alert Comments'].replace('\n',' ')
				document.append(template)
		# print len(document)
		# print document[0]
		# print "\n"
		# print document[0]['Ticket Number']
		# print self.strip_tags(document[0]['Comments'])
		
		dbinter = CouchInterface()

		print "Uploading tickets to database"
		dbinter.add_documents('triager_tickets', document)
		print "Upload Complete"

	###Use these functions only if data is available in the database
	# def predict_category() #Predict the category field of unknown category tickets
		


tkt = Tickets()
tkt.upload_tickets()
