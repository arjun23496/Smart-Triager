import category_learner
import os

def neural_network_learn():
	test_file_list = [ '06_July_2017' ]
	train_file_list = [ '06_July_2017' ]

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
	category_learner.neural_network_test()

	directory_list = [ 'data/test_tickets', 'data/tickets', 'data/test_preprocessed', 'data/preprocessed' ]

	print "Removing Files"
	for directory in directory_list:
		file_list = os.listdir(directory)
		for file in file_list:
			os.remove(directory+"/"+file)

	print "Execution successfully completed"

neural_network_learn()