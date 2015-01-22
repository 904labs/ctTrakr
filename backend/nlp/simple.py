from nltk.tokenize import word_tokenize, sent_tokenize


def tokenize(**kwargs):
	"""Tokenize text using nltk's tokenizer."""

	if 'text' in kwargs.keys():
		return word_tokenize(kwargs['text'])

	return None


def sentence_split(**kwargs):
	"""Split sentences using nltk."""

	import nltk.data

	tokenizer = nltk.data.load('tokenizers/punkt/dutch.pickle')

	if 'text' in kwargs.keys():
		return tokenizer.tokenize(kwargs['text'])

	return None