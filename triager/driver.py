from preprocessor import Tickets
# from utility import WatsonInterface
from sklearn.externals import joblib

import category_learner
import severity_learner
import progressbar
import transformations
import scheduler

######################################## preprocessor testing script

# tkt = Tickets()

# print "uploading xlsx file"
# tkt.upload_tickets_xlsx()

# print "uploading csv tickets"
# tkt.upload_tickets_csv()

######################################## category learner testing
# predictors = category_learner.trainer(restrict_prediction=True, restricted_categories=['S - PER - New Map', 'S - Map Research', 'S - Map Change', 'S - PER - Map Change'])

# joblib.dump(predictors[0], 'predictors/category/transformer.pkl')
# joblib.dump(predictors[1], 'predictors/category/learner.pkl')

######################################## severity learner testing
# predictors = severity_learner.trainer('severity',restrict_prediction=False) #test severity

# joblib.dump(predictors[0], 'predictors/severity/transformer.pkl')
# joblib.dump(predictors[1], 'predictors/severity/learner.pkl')

#text emotion extractor

# corpus = '''Hi Mapping Team,
 
# The issue still persists with the Qty value. 
# Currently in ASN data we are sending SN102 value for all lines as 60 it should be 5.Could you tell me in this scenario from where SN102 value is populating? 
 
# Attached the file from Production for testing. Attached the current output and expected output(Comment(29)). 
 
# Note: Please assign the ticket to Dipayan if possible. 
 
# Thanks, 
# Madhu'''

# WatsonInterface.analyse_text_tone_analyser(corpus)

# couchi = CouchInterface()
# dataf = pd.DataFrame(couchi.get_all_documents('triager_tickets'))

######################################### Transformer testing

date_now = {
		"year": "2016",
		"date": "21",
		"month": "12"
	}

scheduler.execute(date_now)