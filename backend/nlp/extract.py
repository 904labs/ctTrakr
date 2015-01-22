import re
from nlp import simple
from data import scores


def pattern_based(**kwargs):
	"""Extract scores based on string patterns.
	Results in high precision, but is likely to lower recall.
	"""

	if 'text' not in kwargs.keys() or 'metric' not in kwargs.keys():
		return None

	extracted = _extraction(kwargs['metric'], kwargs['text'], "patterns")

	return extracted


def score_based(**kwargs):
	"""Extract scores based on occurrence of the score name and synonyms.
	Results in high recall, but could potentially harm precision.
	"""

	if 'text' not in kwargs.keys() or 'metric' not in kwargs.keys():
		return None

	extracted = _extraction(kwargs['metric'], kwargs['text'], "synonyms")

	return extracted


def two_stage(**kwargs):
	"""Extract scores based in two stages.
	First tries to use patterns, if it does not get a result, it uses score name and synonyms.
	"""

	pattern_extraction = pattern_based(**kwargs)
	if pattern_extraction is not None:
		return pattern_extraction

	score_extraction = score_based(**kwargs)
	if score_extraction is not None:
		return score_extraction

	return None


def _extraction(metric, text, search_type):
	score_data = None
	try:
		score_data = scores.metrics[metric]
	except KeyError:
		print "Metric does not exist"
		return None

	sentences = simple.sentence_split(text=text)

	# find matching sentence
	search_strings = []
	try:
		search_strings = score_data[search_type]
	except KeyError:
		print "Search strings " + search_type + " does not exist"
		return None

	match = _find_sentence(sentences, search_strings)
	if match is None:
		return None

	score = _extract_value(match, score_data['values'])
	if score is None:
		return None	

	return {metric : score}


def _find_sentence(sentences, metrics):
	search_string = "(" + "|".join(metrics) + ")"
	pattern = re.compile(r'%s'%search_string, flags=re.IGNORECASE|re.UNICODE|re.MULTILINE|re.DOTALL)

	for sentence in sentences:
		if _contains_metric_name(pattern, sentence) is not None:
			return sentence

	return None


def _contains_metric_name(pattern, text):
	return pattern.search(text)


def _extract_value(sentence, value_characteristics):
	pattern  = value_characteristics['format']
	function = value_characteristics['type']

	matches = pattern.finditer(sentence)
	for m in matches:
		try:
			value = function(m.group(0))
			if value >= value_characteristics['min'] and value <= value_characteristics['max']:
				return value
		except ValueError:
			continue

	return None
