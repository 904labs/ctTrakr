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
			'format' : re.compile(r'(\-*\d+)((,|\.)\d+)?', flags=re.MULTILINE|re.DOTALL|re.IGNORECASE|re.UNICODE)
		},

		'patterns' : [
			'agatston score van',
			'agatstonscore',
			'agatston score is',
			'agatston kalk score bedraagt',
			'agatston score bedraagt',
			'agatston score',
			'calciumscore meet',
			'agatston kalk score',
			'kalkscore meet',
			'calciumscore bedraagt',
			'agatston kalkscore bedraagt',
			'agatston-score',
			'cororaire kalkscore bedraagt',
			'agatston kalkscore',
			'agatston van'
		]
	}
}