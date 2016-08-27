import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import unicodedata
import scipy as sp
import pydot

from sklearn.cross_validation import train_test_split
from sklearn.base import BaseEstimator, TransformerMixin


from sklearn.preprocessing import *
from sklearn.feature_extraction import *
from sklearn.feature_extraction.text import *
from sklearn.feature_selection import *
from sklearn.pipeline import FeatureUnion,Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import BayesianRidge
from sklearn import tree
from sklearn.externals import joblib
from sklearn import metrics
# from IPython.display import Image 
from sklearn.externals.six import StringIO

# Transformer to convert the values of a specified categorical feature to consecutive integers
class RemoveUnwantedCols(BaseEstimator, TransformerMixin):
    def __init__(self,cols):
        self.cols = cols

    def transform(self, X):
        [X.drop(x,axis=1,inplace=True) for x in self.cols]
        return X

    def fit(self, X, y=None):
        return self

class MissingStringValueSubstituter(BaseEstimator, TransformerMixin):
    def __init__(self,cols):
        self.cols = cols

    def transform(self, X):
    	for x in self.cols:
    		X[x]=X[x].astype(str)
    		X[x]=X[x].replace('nan','')
        return X

    def fit(self, X, y=None):
        return self

class MissingValueImputer(BaseEstimator,TransformerMixin):
    
    def __init__(self,col=None):
        self.mean=0;
        self.col=col
    
    def transform(self,X):
        X[self.col]=X[self.col].fillna(self.mean)
        return X
    
    def fit(self,X,y=None):
        # self.mean = X[self.col].mean()
        return self


##########################################Main function start#####################

#data import

ticket_list=pd.read_csv('data/ticket.csv',header=0);
total_time_spend=pd.read_csv('data/totalTimeSpent.csv',header=2);

#ticket list sanitizer
ticket_list=ticket_list.set_index(pd.Series(range(0,ticket_list.shape[0])));
RemoveUnwantedCols([u'Unnamed: 1']).fit_transform(ticket_list)
MissingStringValueSubstituter([u'Assigned To',u'L3 Ticket']).fit_transform(ticket_list)

#total time spent sanitizer
tts_columns = pd.Series(total_time_spend.columns)
tts_columns[0] = "Resource"
total_time_spend.columns = tts_columns
total_time_spend = MissingStringValueSubstituter([u'Remarks']).fit_transform(total_time_spend)
total_time_spend = MissingValueImputer('Non-work days (Leaves/ trainings)').fit_transform(total_time_spend)
total_time_spend = MissingValueImputer('Net work days/ employee').fit_transform(total_time_spend)

