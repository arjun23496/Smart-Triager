import pandas as pd
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


def category_imputer(df, index):
	categories = ['S - PER - New Map', 'S - Map Research', 'S - Map Change', 'S - PER - Map Change']
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