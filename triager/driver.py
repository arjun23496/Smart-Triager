from preprocessor import Tickets
# import category_learner
import category_learner_randomize

## preprocessor testing script

# tkt = Tickets()

# print "uploading xlsx file"
# tkt.upload_tickets_xlsx()

# print "uploading csv tickets"
# tkt.upload_tickets_csv()

## category learner testing
# category_learner_randomize.trainer(restrict_prediction=True, restricted_categories=['S - PER - New Map', 'S - Map Research', 'S - Map Change', 'S - PER - Map Change']) #naive imple
category_learner_randomize.trainer('severity',restrict_prediction=False) #naive impley
# trainer('severity')