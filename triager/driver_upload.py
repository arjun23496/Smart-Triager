from preprocessor import Tickets
# from utility import WatsonInterface
from sklearn.externals import joblib

import category_learner
import severity_learner
import progressbar
import transformations
import scheduler

######################################## preprocessor testing script

tkt = Tickets()

print "uploading xlsx file"
tkt.upload_tickets_xlsx()

print "uploading csv tickets"
tkt.upload_tickets_csv()