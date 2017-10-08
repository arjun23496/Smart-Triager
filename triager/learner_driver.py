import category_learner_nn as category_learner
import os
import pandas as pd
import numpy as np
import json

def neural_network_learn():
	test_file_list = [ 'ticket_list' ]
	train_file_list = [ 'ticket_list' ]

	#Test and evaluate neural network
	print "Evaluate pre train network"
	category_learner.structure_data(test_file_list, directory="data/test_tickets/")
	category_learner.preprocess_and_save(ticket_directory="data/test_tickets/", save_directory="data/test_preprocessed/", learn=False)
	category_learner.neural_network_test()
	print "End Evaluation of pre trained network"

	print "Training network"
	category_learner.structure_data(train_file_list)
	category_learner.preprocess_and_save(learn=False)
	category_learner.neural_network_trainer(resume_training=True)

	print "Post Train Evaluation"
	evaluation = category_learner.neural_network_test()

	print "Saving Debug info"
	date = ""
	with open(os.path.join(os.path.dirname(__file__),'data/scheduler_date.json'), 'rb') as fp:
		date = json.load(fp)
		date = date['date']+"/"+date['month']+"/"+date['year']

	evaluation.append(date)
	evaluation = [ evaluation ]
	evaluation = np.array(evaluation)
	evaluation_df = pd.DataFrame(evaluation, columns=['loss','accuracy','date'])
	print evaluation_df

	if os.path.isfile('report/neural_net.csv'):
		df = pd.read_csv('report/neural_net.csv')
		evaluation_df = evaluation_df.append(df, ignore_index=True)

	evaluation_df = evaluation_df[ ['loss', 'accuracy', 'date'] ]
	evaluation_df.to_csv('report/neural_net.csv')

	directory_list = [ 'data/test_tickets', 'data/tickets', 'data/test_preprocessed', 'data/preprocessed' ]

	print "Removing Files"
	for directory in directory_list:
		file_list = os.listdir(directory)
		for file in file_list:
			os.remove(directory+"/"+file)

	print "Execution successfully completed"

neural_network_learn()