import json
import progressbar

from utility import WatsonInterface
from utility.CouchInterface import CouchInterface

def alchemy_retrieve():
	couchi = CouchInterface()
	docs = couchi.get_all_documents('triager_tickets')
	bar = progressbar.ProgressBar(maxval=len(docs), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
	bar.start()

	success = 0
	doc = []

	for x in range(0,len(docs)):
		try:
			wat_out = WatsonInterface.analyse_text_alchemy(docs[x]['comments'])
			success = success+1
			doc.append(wat_out)
			f_handle = open('retrieved_data/alchemy','w')
			f_write = '$$$'.join(doc)
			f_handle.write(f_write)
			f_handle.close()
		except Exception:
			pass
		bar.update(x+1)

	bar.finish()

	print success,"/",len(docs)," successful"


def ta_retrieve():
	couchi = CouchInterface()
	docs = couchi.get_all_documents('triager_tickets')
	bar = progressbar.ProgressBar(maxval=len(docs), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
	bar.start()

	success = 0
	doc = []

	for x in range(0,len(docs)):
		try:
			wat_out = WatsonInterface.analyse_text_tone_analyser(docs[x]['comments'])
			success = success+1
			doc.append(wat_out)
			f_handle = open('retrieved_data/tone_analyser','w')
			f_write = '$$$'.join(doc)
			f_handle.write(f_write)
			f_handle.close()
		except Exception:
			pass
		bar.update(x+1)

	bar.finish()
	print success,"/",len(docs)," successful"

print "Retrieve alchemy data"
# alchemy_retrieve()
print "Completed retrieving alchemy data"

print "Retrieve tone anlyser data"
ta_retrieve()
print "Completed retrieving tone analyser data"