import re

metrics = {
	'agatston' : {
		'synonyms' : [
			'agatston',
			'agatston-score',
			'agatstonscore',
			'kalkscore',
			'calciumscore'
		], 

		'values' : {
			'type' : int,
			'min' : 0,
			'max' : 9999,
			'format' : re.compile(r'(\-*\d+)((,|\.)\d+)?', flags=re.MULTILINE|re.DOTALL|re.IGNORECASE|re.UNICODE),
			'group' : 0
		}
	},

	'onderdruk' : {
		'synonyms' : [
			'bloeddruk',
			'bloed druk',
			'tensie'
		], 

		'values' : {
			'type' : int,
			'min' : 0,
			'max' : 250,
			'format' : re.compile(r'\b\d{2,3}\/(\d{2,3})\b', flags=re.MULTILINE|re.DOTALL|re.IGNORECASE|re.UNICODE),
			'group' : 1
		},
	},

	'bovendruk' : {
		'synonyms' : [
			'bloeddruk',
			'bloed druk',
			'tensie'
		], 

		'values' : {
			'type' : int,
			'min' : 0,
			'max' : 250,
			'format' : re.compile(r'\b(\d{2,3})\/\d{2,3}\b', flags=re.MULTILINE|re.DOTALL|re.IGNORECASE|re.UNICODE),
			'group' : 1
		}
	}
}