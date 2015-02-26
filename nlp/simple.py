import nltk.data

from nltk.tokenize import word_tokenize, sent_tokenize
from util import errors, cleaning


def tokenize(**kwargs):
	"""Tokenize text using nltk's tokenizer."""

	if 'text' in kwargs.keys():
		return word_tokenize(kwargs['text'])

	raise errors.CustomAPIError('No text argument found.', status_code=400, payload={'arguments':kwargs.keys()})

def sentence_split(**kwargs):
	"""Split sentences using nltk."""

	tokenizer = nltk.data.load('tokenizers/punkt/dutch.pickle')

	if 'text' in kwargs.keys():
		cleaner = cleaning.Clean()
		cleaner.feed(kwargs['text'])
		cleanedText = cleaner.get_data()

		return tokenizer.tokenize(cleanedText)


	raise errors.CustomAPIError('No text argument found.', status_code=400, payload={'arguments':kwargs.keys()})