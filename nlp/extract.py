import re
from nlp import simple
from util import errors

type_functions = {'int':int, 'float':float }

def health_scores(**kwargs):
	"""
	Extract health scores based on occurrence of the score name and synonyms.
	Test potential values against a set of constraints (min, max, type, and format).
	"""

	if 'text' not in kwargs.keys():
		raise errors.CustomAPIError('No text argument found.', status_code=400, payload={'arguments':kwargs.keys()})

	if 'health_scores' not in kwargs.keys():
		raise errors.CustomAPIError('No health_scores argument found.', status_code=400, payload={'arguments':kwargs.keys()})

	return _extraction_wtr(kwargs['health_scores'], kwargs['text'])


def _extraction_wtr(metrics, text):
	sentences = simple.sentence_split(text=text)

	result = {
		"findings"  : {}
		"sentences" : sentences
	}

	found_scores = {}

	# search for scores, only move forward with the ones we actually find in text
	search_metrics = {}
	patterns = {}

	for m in metrics:
		## UGLY HACK TO GET CONSTRAINTS IN CODE
		defaultValues = _characteristics(m)
		if defaultValues:
			metrics[m]['values'] = defaultValues
		## END OF HACK

		# No synonyms given
		if len(metrics[m]['synonyms']) == 0:
			found_scores[m] = []
			continue

		pattern = create_pattern("(" + "|".join(metrics[m]['synonyms']) + ")")

		# No synonym found
		if pattern.search(text) is None:
			found_scores[m] = []
			continue

		patterns[m] = pattern
		search_metrics[m] = metrics[m]
		found_scores[m] = []

	for index, s in enumerate(sentences):
		for m in search_metrics:
		# check if sentence contains any of the metrics
			match = patterns[m].search(s)
			if match is None:
				continue

			# If no 'value' object, only look for the term
			# to get start / end position in sentence
			found = {
				'sentenceNr' : index,
				'term'       : match.group(0),
				'start'      : match.start(0),
				'end'        : match.end(0)
			}

			if 'values' in metrics[m]:
				matching_score = _extract_value_wtr(s, search_metrics[m], match)
				found.update(matching_score)

			found_scores[m].append(found)


	# Merge scores if we find the same score for one metric multiple times; status "certain"
	# Store all scores if we find different scores for one metric; status "uncertain"

	for m in found_scores:
		unique_scores = set()

		for score in found_scores[m]:
			if 'values' in score:
				unique_scores.update(score['values'])

		result["findings"][m] = found_scores[m]

	return result


def create_pattern(text):
	return re.compile(r'%s'%text, flags=re.MULTILINE|re.DOTALL|re.IGNORECASE|re.UNICODE)

def _extract_value_wtr(sentence, value_characteristics, match):
	checks = {
		'type' : False,
		'min'  : False,
		'max'  : False
	}

	# Determine pattern to use for score finding
	pattern  = create_pattern("([-+]?\d+([,.]\d+)?)")
	if "format" in value_characteristics['values']:
		pattern  = create_pattern(value_characteristics['values']['format'])

	# Group within the MatchObject that contains the score
	group = 0
	if "group" in value_characteristics['values']:
		group = value_characteristics['values']['group']

	# Type of the score (int, float)
	if "type" in value_characteristics['values']:
		checks['type'] = True
		try:
			function = type_functions[value_characteristics['values']['type']]
		except KeyError:
			raise errors.CustomAPIError('Invalid value type', status_code=400, payload={'value type':value_characteristics['values']['type']})

		# Get minimum value for score (only works with a type)
		if "min" in value_characteristics['values']:
			checks['min'] = True
			minimum_value = value_characteristics['values']['min']

		# Get maximum value for score (only works with a type)
		if "max" in value_characteristics['values']:
			checks['max'] = True
			maximum_value = value_characteristics['values']['max']

	# Determine start and end point to search for the score
	# TODO this should be matches in words? Or atleast split on proper boundaries
	#			 and not the middle of a word or number
	start = 0
	end   = len(sentence)
	if "position" in value_characteristics['values']:
		start = match.start(0) + value_characteristics['values']['position']['before']
		end   = match.end(0) + value_characteristics['values']['position']['after']


	# Values not matching the criteria get a warning
	optional_scores = list()

	temp_score = None
	min_diff   = 100000

	matches = pattern.finditer(sentence[start : end])
	for m in matches:
		# Replace commas by decimals (for floats)
		temp_value = m.group(group).replace(',', '.', 1)

		# Find the difference between the found score and the position of the score's name
		difference = 100000
		if m.start(group)+start < match.start(0):
			difference = match.start(0) - (start+m.end(group))
		elif m.start(group)+start > match.start(0):
			difference = m.start(group)+start - match.end(0)

		# Try to convert score to requested type (if needed)
		if checks['type']:
			try:
				value = function(temp_value)

			except ValueError:
				optional_scores.append({
					"value"   : temp_value,
					"warning" : "Value error"
				})
				continue

			if checks['min'] and value < minimum_value:
				optional_scores.append({
					"value"   : value,
					"warning" : "Value too low"
				})

				continue

			if checks['max'] and value > maximum_value:
				optional_scores.append({
					"value"   : value,
					"warning" : "Value too high"
				})

				continue

			temp_value = value

		# Only store score closest to score's name
		if difference < min_diff:
			temp_score = temp_value
			min_diff = difference

	return {
		"value" 	 : temp_score,
		"optional" : optional_scores
	}


## HACK FOR KNOWN SCORES
def _characteristics(metric):
	chars = {
		'agatston' : {
			'values' : {
				'type' : "int",
				'min' : 0,
				'max' : 9999,
				'format' : "([-+]?\d+([,.]\d+)?)",
				'group' : 0,
				'position' : {
					'before' : 0,
					'after' : 40
				}
			}
		},
		'mesa' : {
			'values' : {
				'type' : "int",
				'min' : 0,
				'max' : 100,
				'format' : "\D(\d+)\D",
				'group' : 1,
				'position' : {
					'before'  : -10,
					'after' : 35
				}
			}
		}
	}

	if metric in chars:
		return chars[metric]['values']

	return False
