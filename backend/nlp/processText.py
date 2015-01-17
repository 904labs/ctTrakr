from nltk import word_tokenize, sent_tokenize

def tokenizeText(text):
  tokens = word_tokenize(text)
  return(tokens)

def segmentSentences(text):
  sentences = sent_tokenize(text)
  return(sentences)

def searchTermSnippets(text, search_term):
  print('\n', search_term, '\n')
  terms = searchTerm(text, search_term)
  for term in terms:
    snippets(text, term)
  for term in terms:
    term['highlightedSnippet'] = highlightTermInSnippet(term['snippet'], term['term'])
    term['highlightedSnippetXL'] = highlightTermInSnippet(term['snippetXL'], term['term'])
  return(terms)

def searchTerm(text, search_term):
  results     = []
  startIndex  = 0
  length      = len(search_term)

  while True:
    termStart = text[startIndex:].find(search_term)
    if termStart == -1:
      break
    termEnd   = text[startIndex:].find(search_term) + length
    termIndex = text[startIndex:][termStart:termEnd]

    result = {
      'term'  : termIndex,
      'start' : termStart + startIndex,
      'end'   : termEnd + startIndex
    }

    results.append(result)

    startIndex = startIndex + termStart + 1

  return(results)

def snippets(text, term):
  snippetLength   = 40
  snippetXLFactor = 4

  if term['start'] - snippetLength < 0:
    startSnippet  = 0
  else:
    startSnippet  = term['start'] - snippetLength

  if term['end'] + snippetLength > len(text):
    endSnippet = len(text)
  else:
    endSnippet    = term['end'] + snippetLength

  if term['start'] - snippetLength*snippetXLFactor < 0:
    startSnippetXL  = 0
  else:
    startSnippetXL  = term['start'] - snippetLength*snippetXLFactor

  if term['end'] + snippetLength*snippetXLFactor > len(text):
    endSnippetXL = len(text)
  else:
    endSnippetXL    = term['end'] + snippetLength*snippetXLFactor

  term['startSnippet']  = startSnippet
  term['endSnippet']    = endSnippet
  term['snippet']       = '...'+ text[startSnippet:endSnippet] + '...'

  term['startSnippetXL']  = startSnippetXL
  term['endSnippetXL']    = endSnippetXL
  term['snippetXL']       = '...'+ text[startSnippetXL:endSnippetXL] + '...'

def highlightTermInSnippet(snippet, term):
  highlightedSnippet = snippet.replace(term, '<em>' + term + '</em>')
  return(highlightedSnippet)
