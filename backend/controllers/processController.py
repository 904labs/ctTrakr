from flask.ext.restful import Resource, reqparse
from nlp.processText import tokenizeText, segmentSentences, searchTermSnippets

parser = reqparse.RequestParser()
parser.add_argument('text', type = str, location = 'json',
  required = True)
parser.add_argument('options', type = dict, location = 'json',
  required = True)
parser.add_argument('search_term', type = str, location = 'json',
  required = False)

class ProcessText(Resource):
  def post(self):
    args = parser.parse_args()
    return(processOptions(args))

def processOptions(args):
  results = {}

  if args['options']['tokenize_words']:
    results['Tokens'] = tokenizeText(args['text'])
  if args['options']['segment_sentences']:
    results['Sentences'] = segmentSentences(args['text'])
  if args['options']['search_term']:
    results['SearchTermSnippets'] = searchTermSnippets(args['text'], args['search_term'])

  return(results)