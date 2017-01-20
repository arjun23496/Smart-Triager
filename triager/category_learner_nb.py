import math

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy.sparse import csr_matrix, find
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import *
from sklearn.feature_selection import *
from sklearn.pipeline import FeatureUnion,Pipeline
from sklearn import metrics

#learners
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import GaussianNB

from utility.CouchInterface import CouchInterface

########################################## Transformers ##########################

class ConvertCategoricalToInteger(BaseEstimator, TransformerMixin):
    def __init__(self, col=None):
        self.col = col
        self.categories = []

    def transform(self, X):
        X[self.col] = pd.Categorical.from_array(X[self.col],categories=self.categories).codes
        return X

    def fit(self, X, y=None):
        self.categories = pd.unique(X[self.col])
        return self


class ColumnSelector(BaseEstimator,TransformerMixin):
    def __init__(self, col):
        self.col = col
        
    def transform(self, X):
        return X[self.col]

    def fit(self, X, y=None):
        return self

class ConvertDFToVector(BaseEstimator,TransformerMixin):
    def transform(self,X):
        a = np.ravel(X.values)
        return a
    def fit(self, X, y=None):
        return self

class ConvertSparseToDense(BaseEstimator, TransformerMixin):
    def transform(self,X):
        return X.toarray()

    def fit(self, X, y=None):
        return self

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

def trainer(predict_field='category'):

    couchi = CouchInterface()
    dataf = pd.DataFrame(couchi.get_all_documents('triager_tickets'))

    dataf_train = []
    dataf_test = []
    
    #Test-train-split
    categories = pd.unique(dataf[predict_field])

    min = None
    for x in categories:
        i = len(dataf[dataf[predict_field] == x])
        if i < min or min == None:
            min = i

    split = int(math.floor(0.6*min))

    for x in categories:
        dataf_train.append(dataf[dataf[predict_field] == x][0:split])
        dataf_test.append(dataf[dataf[predict_field] == x][split:])

    dataf_train = pd.concat(dataf_train)
    dataf_test = pd.concat(dataf_test)

    vectorizer = TfidfVectorizer(analyzer='word',lowercase=True, max_df=0.90, min_df=1, stop_words='english', decode_error='ignore')
    terms_tfidf = vectorizer.fit_transform(dataf_train['comments'])

    #Classifier Architecture

    # learner = LinearSVC()
    learner = GaussianNB()

    # Feature selection transformer
    feature_selector = SelectKBest(score_func=chi2,k=50)

    comments_extractor = Pipeline([
                            ('selector', ColumnSelector('comments')),
                            ('tf-idf', TfidfVectorizer(analyzer='word',lowercase=True, max_df=0.90, min_df=1, stop_words='english', decode_error='ignore'))
                        ]);

    detail_extractor = Pipeline([
                            ('selector', ColumnSelector('detail')),
                            ('tf-idf', TfidfVectorizer(analyzer='word',lowercase=True, max_df=0.90, min_df=1, stop_words='english', decode_error='ignore'))
                        ]);

    all_feature_extractor = FeatureUnion([
                            ('extractor1', comments_extractor),
                            ('extractor2', detail_extractor)
                        ]);

    clf_pipeline = Pipeline([
                            ('feature_extractor_pre', all_feature_extractor),
                            ('sparse_to_dense', ConvertSparseToDense()),
                            ('feature_selector', feature_selector),
                            ('learner', learner)
                        ])

    target_transformer = Pipeline([
                            ('label_converter', ConvertCategoricalToInteger(predict_field)),
                            ('df_to_vector', ConvertDFToVector())
                        ])

    actual_Y = {}
    dataf_train_X = dataf_train[['detail','comments']]
    dataf_test_X = dataf_test[['detail','comments']]
    dataf_train_Y = dataf_train[[predict_field]]
    dataf_test_Y = dataf_test[[predict_field]]

    actual_Y['train'] = target_transformer.fit_transform(dataf_train_Y)
    actual_Y['test'] = target_transformer.fit_transform(dataf_test_Y)

    print 'target transformation complete'

    print 'model training started'
    print dataf_train.shape
    print actual_Y['train'].shape
    learned_model = clf_pipeline.fit(dataf_train_X,actual_Y['train'])
    # learned_model = learner.fit(learned_model, actual_Y['train'])
    print 'model training complete'

    pred_prob_Y = {}
    pred_prob_Y['train'] = clf_pipeline.predict(dataf_train)
    pred_prob_Y['test'] = clf_pipeline.predict(dataf_test)

    print pred_prob_Y['train']
    print actual_Y['train']
    print pred_prob_Y['test']
    print actual_Y['test']

    multiclass_classification_metrics_report(actual_Y,pred_prob_Y,['train','test'],0.6)
    # classification_metrics_report(actual_Y,pred_prob_Y,['train','test'],0.6)

trainer('severity')