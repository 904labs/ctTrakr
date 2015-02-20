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
			result["findings"][m] = found_scores[m][0]
			result["findings"][m]['confidence'] = "certain"
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
	check_constraints = False
	pattern  = create_pattern("(\-*\d+)((,|\.)\d+)?")
	group    = 0
	start    = 0
	end      = len(sentence)

	if "values" in value_characteristics:
		pattern  = create_pattern(value_characteristics['values']['format'])

		try:
			function = type_functions[value_characteristics['values']['type']]
		except KeyError:
			raise errors.CustomAPIError('Invalid value type', status_code=400, payload={'value type':value_characteristics['values']['type']})

		group = value_characteristics['values']['group']

		start = match.start(0) + value_characteristics['values']['position']['before']
		end   = match.end(0) + value_characteristics['values']['position']['after']

		check_constraints = True


	result = []
	temp_score = None
	min_diff = 100000

	matches = pattern.finditer(sentence[start : end])
	for m in matches:
		temp_value = re.sub(r'(\d),(\d)', '\1\.\2', m.group(group))

		difference = 0
		if m.start(group)+start < match.start(0):
			difference = match.start(0) - (start+m.end(group))
		elif m.start(group)+start > match.start(0):
			difference = m.start(group)+start - match.end(0)

		try:
			if not check_constraints:
				if difference < min_diff:
					temp_score = temp_value
					min_diff = difference
				continue

			value = function(temp_value)
			if value >= value_characteristics['values']['min'] and value <= value_characteristics['values']['max']:
				if difference < min_diff:
					temp_score = temp_value
					min_diff = difference
				continue
		except ValueError:
			continue

	if temp_score is None:
		return None

	result.append(temp_score)
	return result
