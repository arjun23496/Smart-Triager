import pandas as pd
import datetime
from sklearn.externals import joblib

def new_value_imputer(df,index,ticket_number):
	q_list=df[df['ticket_number']==ticket_number]['new_queue'][1:index]
	val = ''
	for x in q_list:
		if x != '' or None:
			val = x

	return val


def category_imputer(df,index):
	categories = ['S - PER - New Map', 'S - Map Research', 'S - Map Change', 'S - PER - Map Change']
	transformer=joblib.load('./predictors/category/transformer.pkl')
	learner=joblib.load('./predictors/category/learner.pkl')
	
	transformed_df = transformer.transform(df.loc[index:index])
	pred_res = learner.predict(transformed_df)
	pred_res = categories[pred_res[0]]

	return pred_res


def category_imputer(df, index, ticket_number,action_date,ticket_dtime_format):
	categories = ['S - PER - New Map', 'S - Map Research', 'S - Map Change', 'S - PER - Map Change']
	
	df = df[df['ticket_number'] == ticket_number]
	ptdate = datetime.datetime.strptime(action_date, ticket_dtime_format)
	maxdate = ''
	maxcategory = ''

	for index, row in df.iterrows():
		tdate = datetime.datetime.strptime(row['action_date'], ticket_dtime_format)
		if (row['category']!='' and (not pd.isnull(row['category'])) and row['category'] in categories) and (maxdate == '' or (ptdate>tdate and tdate>maxdate)):
			maxdate = tdate
			maxcategory = row['category']

	if maxcategory!='':
		print "Assigned category using ticket history"
		return maxcategory

	transformer=joblib.load('./predictors/category/transformer.pkl')
	learner=joblib.load('./predictors/category/learner.pkl')
	
	transformed_df = transformer.transform(df.loc[index:index])
	pred_res = learner.predict(transformed_df)
	pred_res = categories[pred_res[0]]

	return pred_res


def severity_imputer(df, index):
	severities = ["Sev 2", "Sev 3", "Sev 4", ]
	transformer=joblib.load('./predictors/severity/transformer.pkl')
	learner=joblib.load('./predictors/severity/learner.pkl')
	
	transformed_df = transformer.transform(df.loc[index:index])
	pred_res = learner.predict(transformed_df)
	# pred_res = severities[pred_res[0]]
	category = df.loc[index:index]['category'][index]
	
	if pred_res == 0:
		if category == 'S - PER - New Map':
			pred_res = 2
		else:
			pred_res = 1
	else:
		pred_res = 0

	return severities[pred_res]