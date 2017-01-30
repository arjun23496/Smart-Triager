import json
from watson_developer_cloud import AlchemyLanguageV1
from watson_developer_cloud import ToneAnalyzerV3

def analyse_text_alchemy(text):
	alchemy_language = AlchemyLanguageV1(api_key='9d6d5a8f90a3fed2f5e1792865dbf4124daa9a70')
	# print "Querying Watson Service..."
	a = json.dumps(alchemy_language.combined(text=text, extract='entities,keywords,doc-emotion,doc-sentiment', max_items=1))
	# print a
	return a

def analyse_text_tone_analyser(text):
	tone_analyzer = ToneAnalyzerV3(
	   username='92e83356-4498-41be-8551-1013317083b1',
	   password='4Vy2YHm4zuhD',
	   version='2016-05-19')

	a = json.dumps(tone_analyzer.tone(text=text))

	return a
