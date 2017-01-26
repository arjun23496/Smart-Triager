from preprocessor import Tickets
import category_learner
import severity_learner

######################################## preprocessor testing script

# tkt = Tickets()

# print "uploading xlsx file"
# tkt.upload_tickets_xlsx()

# print "uploading csv tickets"
# tkt.upload_tickets_csv()

######################################## category learner testing
# category_learner.trainer(restrict_prediction=True, restricted_categories=['S - PER - New Map', 'S - Map Research', 'S - Map Change', 'S - PER - Map Change'])


######################################## severity learner testing
severity_learner.trainer('severity',restrict_prediction=False) #test severity