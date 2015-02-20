import re
from nlp import simple
from util import errors

type_functions = {'int':int, 'float':float}

def health_scores(**kwargs):
	"""
	Extract health scores based on occurrence of the score name and synonyms.
	Test potential values against a set of constraints (min, max, type, and format).
	"""

	if 'text' not in kwargs.keys():
		raise errors.CustomAPIError('No text argument found.', status_code=400, payload={'arguments':kwargs.keys()})

	if 'health_scores' not in kwargs.keys():
		raise errors.CustomAPIError('No health_scores argument found.', status_code=400, payload={'arguments':kwargs.keys()})

	extracted = _extraction_wtr(kwargs['health_scores'], kwargs['text'])
	return extracted


def _extraction_wtr(metrics, text):
	sentences = simple.sentence_split(text=text)
	highlighted = sentences[:] # Clone

	found_scores = {}

	# search for scores, only move forward with the ones we actually find in text
	search_metrics = {}
	patterns = {}
	for m in metrics:

		## UGLY HACK TO GET CONSTRAINTS IN CODE
		metrics[m]['values'] = _characteristics(m)
		## END OF HACK

		pattern = create_pattern("(" + "|".join(metrics[m]['synonyms']) + ")")
		if pattern.search(text) is None:
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

			highlighted[index] = re.sub(patterns[m], r'<em class="highlight">\1</em>', highlighted[index])
			matching_score = _extract_value_wtr(s, search_metrics[m], match)
			if matching_score is None:
				continue

			found_scores[m].append({
				'sentenceNr' : index,
				'values' : matching_score,
				'term' : match.group(0),
				'start' : match.start(0)
			})


	# Merge scores if we find the same score for one metric multiple times; status "certain"
	# Store all scores if we find different scores for one metric; status "uncertain"
	result = {
		"findings" : {}
	}
	for m in found_scores:
		unique_scores = set()
		for score in found_scores[m]:
			unique_scores.update(score['values'])

		if len(unique_scores) == 1:
			result["findings"][m] = [found_scores[m][0]]
		else:
			result["findings"][m] = found_scores[m]

	result["sentences"] = highlighted
	return result


def _extraction(metrics, text):
	sentences = simple.sentence_split(text=text)
	highlighted = sentences[:] # Clone

	result = {}
	found_metrics = {}

	# For each synonym see if it exists in the text
	for m in metrics:
		found_metrics[m] = []

		for term in sorted(metrics[m]['synonyms'], key=len, reverse=True):
			pattern = re.compile(r'(\b)(%s)(\b)' % re.escape(term), flags=re.MULTILINE|re.IGNORECASE|re.UNICODE)

			if not pattern.search(text):
				continue

			# It exists, check each sentence
			# TODO speed up -> use match for an indication of which sentence
			for index, s in enumerate(sentences):
				if not pattern.search(s):
					continue

				# Highlight found term
				highlighted[index] = re.sub(pattern, r'\1<em class="highlight">\2</em>\3', highlighted[index])

				# Find all matches
				for match in re.finditer(pattern, s):
					values_before_match = _extract_value(s[match.start(2) - 30 : match.start(2)], metrics[m])
					values_after_match  = _extract_value(s[match.end(2) : match.end(2) + 30 ],    metrics[m])

					# Combine findings
					values = values_before_match + values_after_match

					found_metrics[m].append({
						"sentenceNr" : index,
						"term"       : term,
						"start"      : match.start(2),
						"values"     : values
					})

		# TODO Filter matches to pick "umbrella" terms

	result["findings"]  = found_metrics
	result["sentences"] = highlighted
	return result


def create_pattern(text):
	return re.compile(r'%s'%text, flags=re.MULTILINE|re.DOTALL|re.IGNORECASE|re.UNICODE)


# TODO
# Allow custom format (no need for min/max here yet)
def _extract_value(sentence, value_characteristics):
	if not "values" in value_characteristics:
		return []

	pattern = create_pattern("(\-*\d+)((,|\.)\d+)?")

	result  = []

	for m in pattern.finditer(sentence):
		if m.group(0):
			result.append(m.group(0))

	return result


def _extract_value_wtr(sentence, value_characteristics, match):
	checks = {
		'type' : False,
		'min' : False,
		'max' : False
	}

	# Determine pattern to use for score finding
	pattern  = create_pattern("(\-*\d+)((,|\.)\d+)?")
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
	start = 0
	end   = len(sentence)
	if "position" in value_characteristics['values']:
		start = match.start(0) + value_characteristics['values']['position']['before']
		end   = match.end(0) + value_characteristics['values']['position']['after']




	temp_score = None
	min_diff   = 100000

	matches = pattern.finditer(sentence[start : end])
	for m in matches:
		# Replace commas by decimals (for floats)
		temp_value = re.sub(r'(\d),(\d)', '\1\.\2', m.group(group))

		print m.group(group)

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
				continue

			if checks['min'] and value < minimum_value:
				continue

			if checks['max'] and value > maximum_value:
				continue

			temp_value = value


		# Only store score closest to score's name
		if difference < min_diff:
			temp_score = temp_value
			min_diff = difference


	if temp_score is None:
		return None

	return [temp_score]


## HACK FOR KNOWN SCORES
def _characteristics(metric):
	chars = {
		'agatston' : {
			'values' : {
				'type' : "int",
				'min' : 0,
				'max' : 9999,
				'format' : "(\-*\d+)((,|\.)\d+)?",
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

	return {}
