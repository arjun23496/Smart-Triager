import math
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy.sparse import csr_matrix, find
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import *
from sklearn.feature_selection import *
from sklearn.pipeline import FeatureUnion,Pipeline
from sklearn import metrics

from utility.CouchInterface import CouchInterface
from mappings.Ticket import csv_mapping

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


def batch_data_preprocessing(data):
    ticket_list = pd.unique(data['ticket_number'])

    for ticket in ticket_list:
        sub_data = data[data['ticket_number'] == ticket]
        main_data = sub_data
        if os.path.isfile('data/tickets/'+ticket+'.csv'):
            main_data = pd.read_csv('data/tickets/'+ticket+'.csv')
            main_data = main_data.append(sub_data, ignore_index=True)
        main_data.drop_duplicates()
        main_data.to_csv('data/tickets/'+ticket+'.csv')


def structure_data(ticket_batch_list):

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
        batch_data_preprocessing(df)

# trainer()
# trainer('severity')