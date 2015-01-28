import re
from nlp import simple
from util import errors

type_functions = {'int':int, 'float':float, 'long':long, 'complex':complex}

def health_scores(**kwargs):
	"""Extract health scores based on occurrence of the score name and synonyms.
	Test potential values against a set of constraints (min, max, type, and format).
	"""

	if 'text' not in kwargs.keys():
		raise errors.CustomAPIError('No text argument found.', status_code=400, payload={'arguments':kwargs.keys()})
	if 'health_scores' not in kwargs.keys():
		raise errors.CustomAPIError('No health_scores argument found.', status_code=400, payload={'arguments':kwargs.keys()})

	extracted = _extraction(kwargs['health_scores'], kwargs['text'])
	return extracted


def _extraction(metrics, text):
	found_scores = {}

	# search for scores, only move forward with the ones we actually find in text
	search_metrics = {}
	patterns = {}
	for m in metrics:
		pattern = create_pattern("(" + "|".join(metrics[m]['synonyms']) + ")")
		if pattern.search(text) is not None:
			patterns[m] = pattern
			search_metrics[m] = metrics[m]
			found_scores[m] = []

	sentences = simple.sentence_split(text=text)

	for s in sentences:
		for m in search_metrics:
		# check if sentence contains any of the metrics
			if _contains_metric_name(patterns[m], s) is not None:
				matching_score = _extract_value(s, search_metrics[m])
				if matching_score is not None:
					found_scores[m].append({'value':matching_score, 'evidence':s})


	return found_scores


def create_pattern(text):
	return re.compile(r'%s'%text, flags=re.MULTILINE|re.DOTALL|re.IGNORECASE|re.UNICODE)


def _contains_metric_name(pattern, text):
	return pattern.search(text)


def _extract_value(sentence, value_characteristics):
	check_constraints = False
	pattern = create_pattern("(\-*\d+)((,|\.)\d+)?")
	group = 0

	if "values" in value_characteristics:
		pattern  = create_pattern(value_characteristics['values']['format'])

		try:
			function = type_functions[value_characteristics['values']['type']]
		except KeyError:
			raise errors.CustomAPIError('Invalid value type', status_code=400, payload={'value type':value_characteristics['values']['type']})

		group    = value_characteristics['values']['group']
		check_constraints = True


	matches = pattern.finditer(sentence)
	for m in matches:
		try:
			if not check_constraints:
				return m.group(group)

			value = function(m.group(group))
			if value >= value_characteristics['values']['min'] and value <= value_characteristics['values']['max']:
				return value
		except ValueError:
			continue

	return None
