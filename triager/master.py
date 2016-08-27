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
    		X[x].astype(str)
    		X[x]=X[x].replace('nan','')
        return X

    def fit(self, X, y=None):
        return self

##########################################Main function start#####################

ticket_list=pd.read_csv('data/ticket.csv',header=0);
ticket_list=ticket_list.set_index(pd.Series(range(0,ticket_list.shape[0])));

RemoveUnwantedCols([u'Unnamed: 1']).fit_transform(ticket_list)
MissingStringValueSubstituter([u'Assigned To',u'L3 Ticket']).fit_transform(ticket_list)

print ticket_list.head()
# print pd.Series(range(0,ticket_list.shape[0]))