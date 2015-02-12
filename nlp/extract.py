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

	extracted = _extraction(kwargs['health_scores'], kwargs['text'])
	return extracted


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


def _contains_metric_name(pattern, text):
	return pattern.search(text)


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
