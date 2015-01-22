import re
from nlp import simple
from data import scores


def health_scores(**kwargs):
	"""Extract health scores based on occurrence of the score name and synonyms.
	Test potential values against a set of constraints (min, max, type, and format).
	"""

	if 'text' not in kwargs.keys() or 'metrics' not in kwargs.keys():
		return None

	extracted = _extraction(kwargs['metrics'], kwargs['text'])

	return extracted


def _extraction(metrics, text):
	reload(scores)

	found_scores = {}

	# search for scores, only move forward with the ones we actually find in text
	search_metrics = {}
	patterns = {}
	for m in metrics:
		score_data = None
		try:
			score_data = scores.metrics[m]
		except KeyError:
			continue
		else:
			search_string = "(" + "|".join(score_data['synonyms']) + ")"
			pattern = re.compile(r'%s'%search_string, flags=re.IGNORECASE|re.UNICODE|re.MULTILINE|re.DOTALL)
			if pattern.search(text) is not None:
				patterns[m] = pattern
				search_metrics[m] = score_data
				found_scores[m] = []

	sentences = simple.sentence_split(text=text)

	for s in sentences:
		for m in search_metrics:
		# check if sentence contains any of the metrics
			if _contains_metric_name(patterns[m], s) is not None:
				matching_score = _extract_value(s, search_metrics[m]['values'])
				if matching_score is not None:
					found_scores[m].append({'value':matching_score, 'evidence':s})


	return found_scores


def _contains_metric_name(pattern, text):
	return pattern.search(text)


def _extract_value(sentence, value_characteristics):
	pattern  = value_characteristics['format']
	function = value_characteristics['type']

	matches = pattern.finditer(sentence)
	for m in matches:
		try:
			value = function(m.group(value_characteristics['group']))
			if value >= value_characteristics['min'] and value <= value_characteristics['max']:
				return value
		except ValueError:
			continue

	return None
