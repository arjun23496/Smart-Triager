import math
import os
import pickle

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.externals import joblib
from sklearn import metrics

from utility.CouchInterface import CouchInterface
from mappings.Ticket import csv_mapping
from neural_network import NeuralNetwork

########################################## Transformers ##########################

#Classification metrics
def multiclass_classification_metrics_report(actual_Y,pred_prob_Y, modes, cutoff):
    for i in modes:
        print "Case: ",i
        labels =actual_Y[i]
        preds =pred_prob_Y[i]
        print preds.shape
        preds_cutoff = preds
        print "Classification Metrics"
        print  metrics.classification_report(labels, preds_cutoff)
        print "Confusion Matrix"
        print metrics.confusion_matrix(labels, preds_cutoff)    
        print "Accuracy is", 100*metrics.accuracy_score(labels,preds_cutoff), "\n"

def classification_metrics_report(actual_Y,pred_prob_Y, modes, cutoff):
    for i in modes:
        print "Case: ",i
        labels =actual_Y[i]
        preds =pred_prob_Y[i]
        print preds.shape
        preds_cutoff = np.array([1 if p>cutoff else 0 for p in preds])
        print "Confusion Matrix at cutoff =",cutoff
        print  metrics.classification_report(labels,preds_cutoff)    
        print "Accuracy at cutoff =",cutoff,"is", 100*metrics.accuracy_score(labels,preds_cutoff)
        print "Area under ROC curve =", metrics.roc_auc_score(labels,preds) 
    plot_pr_curves(actual_Y,pred_prob_Y,modes)    
    plot_auc_curves(actual_Y,pred_prob_Y,modes)


def plot_pr_curves(actual_Y,pred_prob_Y,modes):
    plt.figure()
    for i in modes:
        labels =actual_Y[i]
        preds =pred_prob_Y[i]
        prec,rec,thresh = metrics.precision_recall_curve(labels,preds)
        plt.plot(rec,prec,label=i)
    plt.ylabel("Precision")
    plt.xlabel("Recall")
    plt.title("Precision-Recall Curve")
    plt.legend(loc='best');
    plt.grid(True)
    plt.show()


def plot_auc_curves(actual_Y,pred_prob_Y,modes):
    plt.figure()
    for i in modes:
        labels =actual_Y[i]
        preds =pred_prob_Y[i]
        fpr,tpr,thresh = metrics.roc_curve(labels,preds)
        plt.plot(fpr,tpr,label=i)
    plt.ylabel("True Positive Rate")
    plt.xlabel("False Positive Rate")
    plt.title("ROC-Curve")
    plt.legend(loc='best');
    plt.grid(True)
    plt.show()

##########################################Main function start#####################


def batch_data_preprocessing(data, directory):
    ticket_list = pd.unique(data['ticket_number'])

    for ticket in ticket_list:
        sub_data = data[data['ticket_number'] == ticket]
        main_data = sub_data
        if os.path.isfile(directory+ticket+'.csv'):
            main_data = pd.read_csv(directory+ticket+'.csv')
            main_data = main_data.append(sub_data, ignore_index=True)
        main_data.drop_duplicates()
        main_data.to_csv(directory+ticket+'.csv')


def structure_data(ticket_batch_list, directory='data/tickets/'):

    for filename in ticket_batch_list:
        print "Processing ",filename
        df = pd.read_csv('data/'+filename+'.csv')
        available_cols = []
        mapped_cols = []
        for x in df.columns:
            try:
                mapped_cols.append(csv_mapping[x])
                available_cols.append(x)
            except KeyError:
                pass

        df = df[available_cols]
        df.columns = mapped_cols
        batch_data_preprocessing(df, directory)


def preprocess_and_save(ticket_directory='data/tickets/', save_directory='data/preprocessed/', learn=False):

    #Hyperparameters
    max_features = 1000
    max_df=0.8      #idf threshold
    min_df=0.8        #min idf threshold
    #End Hyperparameters

    file_list = os.listdir(ticket_directory)
    number_of_files = len(file_list)

    useful_columns = [ 'comments', 'detail', 'category' ]

    complete_df = None

    #Learn TF-IDF Features
    print "Find TF IDF Vectors"
    for x in xrange(number_of_files):
        filename = file_list[x]
        # print "Processing ",filename," ",x,"/",number_of_files

        df = pd.read_csv(ticket_directory+filename)
        df = df[useful_columns]

        if x==0:
            complete_df = df
        else:
            complete_df = complete_df.append(df)

    tf_vectorizer_comments = None
    tf_vectorizer_detail = None

    complete_df[complete_df['comments'].isnull()] = ''
    complete_df[complete_df['detail'].isnull()] = ''

    if learn:

        tf_vectorizer_comments = TfidfVectorizer(analyzer='word', max_features=max_features, lowercase=True, stop_words='english', decode_error='ignore')
        tf_vectorizer_detail = TfidfVectorizer(analyzer='word', max_features=max_features, lowercase=True, stop_words='english', decode_error='ignore')    

        tf_vectorizer_comments.fit(complete_df['comments'])
        tf_vectorizer_detail.fit(complete_df['detail'])

        #Save Learned Model
        joblib.dump(tf_vectorizer_comments,'predictors/category/commentstfidf.pkl')
        joblib.dump(tf_vectorizer_detail,'predictors/category/detailtfidf.pkl')
        print "TF-IDF models saved"
    else:
        print "Loading tfidf models"
        tf_vectorizer_comments = joblib.load('predictors/category/commentstfidf.pkl')
        tf_vectorizer_detail = joblib.load('predictors/category/commentstfidf.pkl')

    #Save Data
    print "Transforming and saving inputs"
    for x in xrange(number_of_files):
        filename = file_list[x]
        # print "Transforming and saving ",filename," ",x,"/",number_of_files

        df = pd.read_csv(ticket_directory+filename)
        df = df[useful_columns]

        df[df['category'].isnull()] = "n"
        df[df['comments'].isnull()] = ""
        df[df['detail'].isnull()] = ""

        comment_vectorizer_results = pd.DataFrame(tf_vectorizer_comments.transform(df['comments']).toarray(), columns=tf_vectorizer_comments.get_feature_names())
        detail_vectorizer_results = pd.DataFrame(tf_vectorizer_detail.transform(df['detail']).toarray(), columns=tf_vectorizer_detail.get_feature_names())

        del df['detail']
        del df['comments']

        column_names = ['category']
        column_names.extend(tf_vectorizer_comments.get_feature_names())
        column_names.extend(tf_vectorizer_detail.get_feature_names())

        df = pd.concat([df, comment_vectorizer_results, detail_vectorizer_results], axis=1, ignore_index=True)
        df.columns = column_names
        df.to_csv(save_directory+filename)


def neural_network_test(weight_file='predictors/neural_network/weights.h5'):
    file_list = os.listdir('data/test_preprocessed')
    number_of_files = len(file_list)
    model = NeuralNetwork()

    complete = None

    for x in xrange(number_of_files):
        # print "Processing ",x,'/',number_of_files
        filename = file_list[x]

        df = pd.read_csv('data/test_preprocessed/'+filename)

        if x == 0:
            complete = df
        else:
            complete = complete.append(df, ignore_index=True)

    complete = complete[complete['category'].notnull()]
    complete = complete.values

    X = complete[:,2:]
    y = complete[:,1]

    # print X.shape
    # print y.shape
    # print complete

    categories = { 'S - Map Change': 0, 'S - Mapping Request': 1, 'S - Map Research': 2, 'S - PER - New Map': 3, 'S - PER - Map Change': 4, 'n': 3  }

    def mapping_function(x):
        try:
            return categories[x]
        except KeyError:
            return 4

    mapper = np.vectorize(mapping_function)

    y = mapper(y)

    y_normalized = np.zeros((y.shape[0], 5))
    y_normalized[:, y] = 1

    print "Loading neural network weights"
    model.load_weights(weight_file)

    print "Test Evaluate model"
    evaluation = model.evaluate(X, y_normalized)
    print "Accuracy : ",evaluation[1]
    return evaluation


def neural_network_trainer(train_frac = 0.8, number_of_folds=5, resume_training=False):
    file_list = os.listdir('data/preprocessed')
    number_of_files = len(file_list)

    model = NeuralNetwork()

    if resume_training:
        model.load_weights('predictors/neural_network/weights.h5')

    complete = None

    for x in xrange(number_of_files):
        # print "Processing ",x,'/',number_of_files
        filename = file_list[x]

        df = pd.read_csv('data/preprocessed/'+filename)

        # print df.shape

        if x == 0:
            complete = df
        else:
            complete = complete.append(df, ignore_index=True)

    print "Shuffling and imputing null values"
    complete = complete.sample(frac=1).reset_index(drop=True)
    # complete[complete['category'].isnull()] = 'n'
    # print pd.unique(complete['category'])
    complete = complete.values

    random_index = np.random.choice(range(complete.shape[0]), int(train_frac*complete.shape[0]))
    test_index = [x for x in range(complete.shape[0]) if x not in random_index]

    categories = { 'S - Map Change': 0, 'S - Mapping Request': 1, 'S - Map Research': 2, 'S - PER - New Map': 3, 'S - PER - Map Change': 4, 'n': 3  }

    def mapping_function(x):
        try:
            return categories[x]
        except KeyError:
            return 4

    mapper = np.vectorize(mapping_function)

    print "Creating Test and Train sets"

    X_train = complete[random_index, 2:]
    y_train = complete[random_index, 1]

    y_train = mapper(y_train)
    print y_train

    X_test = complete[test_index, 2:]
    y_test = complete[test_index, 1]

    y_test = mapper(y_test)
    print y_test

    y_train_normalized = np.zeros((y_train.shape[0], 5))
    y_test_normalized = np.zeros((y_test.shape[0], 5))

    print "Convert Categorical y to numpy array"

    y_train_normalized[:,y_train] = 1
    y_test_normalized[:, y_test] = 1

    print "Training Neural Network"
    model.train(X_train, y_train_normalized, epochs=200, batch_size=int(y_train.shape[0]/number_of_folds))

    print "Evaluating test data"
    print model.evaluate(X_test, y_test_normalized, batch_size=int(y_test_normalized.shape[0]/number_of_folds))

    print "Saving Model"
    model.persist_model('predictors/neural_network/weights.h5')
    print "Saved Exiting"