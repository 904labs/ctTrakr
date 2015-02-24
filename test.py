import unittest
import requests
import json

class TestBasicAPI(unittest.TestCase):

	def setUp(self):
		self.data = {"text" : "Example sentences, which can be tokenized. We can also split the sentences. We can extract scores like an agatston score of 432."}
		self.headers = {'Content-Type': 'application/json'}
		self.base_url = "http://127.0.0.1:5000/api/"

	def test_accepted_method(self):
		tasks = ('simple/tokenize','simple/sentence_split','extract/health_scores')

		for task in tasks:
			url    = self.base_url + task
			r      = requests.get(url, data=json.dumps(self.data), headers=self.headers)
			result = r.json()

			# check status code (405)
			self.assertEquals(result['status'], 405)


	def test_endpoint_not_found(self):
		url    = self.base_url + "non_existing"
		r      = requests.post(url, data=json.dumps(self.data), headers=self.headers)
		result = r.json()

		# check status code (404)
		self.assertEquals(result['status'], 404)


	def test_content_type(self):
		tasks = ('simple/tokenize','simple/sentence_split','extract/health_scores')
		self.headers['Content-Type'] = "application/xml"

		for task in tasks:
			url    = self.base_url + task
			r      = requests.post(url, data=json.dumps(self.data), headers=self.headers)
			result = r.json()

			# check status code (415)
			self.assertEquals(result['status'], 415)


	def test_missing_text(self):
		tasks = ('simple/tokenize','simple/sentence_split','extract/health_scores')
		self.data = {"incorrect_label" : "Example sentences, which can be tokenized. We can also split the sentences. We can extract scores like an agatston score of 432."}

		for task in tasks:
			url    = self.base_url + task
			r      = requests.post(url, data=json.dumps(self.data), headers=self.headers)
			result = r.json()

			# check status code (415)
			self.assertEquals(result['status'], 400)


class TestSimpleFunctions(unittest.TestCase):

	def setUp(self):
		self.data = {"text" : "Example sentences, which can be tokenized. We can also split the sentences. We can extract scores like an agatston score of 432."}
		self.headers = {'Content-Type': 'application/json'}
		self.base_url = "http://127.0.0.1:5000/api/simple/"

	def test_tokenize(self):
		url    = self.base_url + "tokenize"
		r      = requests.post(url, data=json.dumps(self.data), headers=self.headers)
		result = r.json()

		# check status code (200)
		self.assertEquals(result['status'], 200)

		# check if result exists in json
		self.assertTrue('result' in result)

		# check if length of the list matches number of tokens
		self.assertTrue(len(result['result']), 26)


	def test_sentence_split(self):
		url = self.base_url + "sentence_split"
		r      = requests.post(url, data=json.dumps(self.data), headers=self.headers)
		result = r.json()

		# check status code (200)
		self.assertEquals(result['status'], 200)

		# check if result exists in json
		self.assertTrue('result' in result)

		# check if length of the list matches number of tokens
		self.assertTrue(len(result['result']), 3)


class TestExtractionFunctions(unittest.TestCase):
	def setUp(self):
		self.data = {"text" : "Example sentences, which can be tokenized met pizza brood voor unknownValue test. The first agatston score is 432 432 (mesa percentiel 22). We can also split the sentences. We can extract scores like an agatston score of 612 which is the 23e MESA percentiel. Other agatston scores are -9 which is too low. Also, for agatston 8,6 is incorrect. Finally, an agatston score of 40000 is too high to be possible. The following agatston is too far away to be considered useful 430."}
		self.health_scores = {
			'agatston' : {
				'synonyms' : [
					'agatston',
					'agatston-score',
					'agatstonscore',
					'kalkscore',
					'calciumscore'
				],

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

			'unknownValue' : {
				'synonyms' : ["pizza", "brood"],
				'values' : {}
			},

			'mesa' : {
				'synonyms' : [
					'MESA'
				],

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

		self.headers = {'Content-Type': 'application/json'}
		self.base_url = "http://127.0.0.1:5000/api/extract/health_scores"

	def test_missing_health_scores(self):
		r      = requests.post(self.base_url, data=json.dumps(self.data), headers=self.headers)
		result = r.json()

		# check status code (415)
		self.assertEquals(result['status'], 400)


	def test_multiple_values_strict(self):
		self.data['health_scores'] = self.health_scores
		r = requests.post(self.base_url, data=json.dumps(self.data), headers=self.headers)
		result = r.json()

		# assert status
		self.assertEquals(result['status'], 200)

		#assert existence of json result
		#print result
		self.assertTrue('result' in result)

		# assert existence of agatston score in result
		self.assertTrue('agatston' in result['result']['findings'])
		self.assertTrue('mesa' in result['result']['findings'])

		# assert correct value of agatston

		self.assertEquals(len(result['result']['findings']['agatston']), 6)

		# First 2 are 'good' findings
		self.assertEquals(432, result['result']['findings']['agatston'][0]['value'])
		self.assertEquals(612, result['result']['findings']['agatston'][1]['value'])

		# Last 4 should be warnings (but still included for highlight / 'incorrect' value display)
		self.assertTrue(-9 in [x['value'] for x in result['result']['findings']['agatston'][2]['optional'] ])

		# assert correct value of mesa
		self.assertEquals(len(result['result']['findings']['mesa']), 2)
		self.assertEquals(22, result['result']['findings']['mesa'][0]['value'])
		self.assertEquals(23, result['result']['findings']['mesa'][1]['value'])


	def test_multiple_values_fuzzy(self):
		self.data['health_scores'] = {
			'agatston' : {
				'synonyms' : [
					'agatston',
					'agatston-score',
					'agatstonscore',
					'kalkscore',
					'calciumscore'
				],
				'values' : {}
			}
		}
		r = requests.post(self.base_url, data=json.dumps(self.data), headers=self.headers)
		result = r.json()

		# assert status
		self.assertEquals(result['status'], 200)

		#assert existence of json result
		self.assertTrue('result' in result)

		# assert existence of agatston score in result
		self.assertTrue('agatston' in result['result']['findings'])

		# assert correct value of agatston
		self.assertEquals(432, result['result']['findings']['agatston'][0]['value'])
		self.assertEquals(612, result['result']['findings']['agatston'][1]['value'])

		## Following values are not in the results, since 'hack' default values

		# Too low
		self.assertTrue(-9 in [x['value'] for x in result['result']['findings']['agatston'][2]['optional']])

		# It is a float, but agatston accepts int, so give warning
		self.assertTrue("8.6" in [x['value'] for x in result['result']['findings']['agatston'][3]['optional']])

		# Too high
		self.assertTrue(40000 in [x['value'] for x in result['result']['findings']['agatston'][4]['optional']])


	def test_nonexistent_type(self):
		self.data['health_scores'] = self.health_scores
		self.data['health_scores']['unknownValue']['values']['type'] = "string"

		r = requests.post(self.base_url, data=json.dumps(self.data), headers=self.headers)
		result = r.json()

		# assert status
		self.assertEquals(result['status'], 400)

	def test_types(self):
		types = ('float','int')
		self.data['health_scores'] = self.health_scores

		for t in types:
			self.data['health_scores']['agatston']['values']['type'] = t
			r = requests.post(self.base_url, data=json.dumps(self.data), headers=self.headers)
			result = r.json()

			# assert status
			self.assertEquals(result['status'], 200)

class TestResultFormatting(unittest.TestCase):
	def setUp(self):
		self.data = {"text" : "RA (rheumatoid antigen) can be positive in several different conditions beyond rheumatoid arthritis.  It can also be incidentally positive without disease.  If it is specifically your muscles hurting and not your joints then rheumatoid arthritis seems a bit less likely for you."}
		self.health_scores = {
			'rheuma' : {
				'synonyms' : [
					"rheumatoid disease",
					"atrofische artritis",
					"rheumatoid arthritis"
				]
			}
		}

		self.headers = {'Content-Type': 'application/json'}
		self.base_url = "http://127.0.0.1:5000/api/extract/health_scores"

	'''
	def test_without_valueDescription(self):
		self.data['health_scores'] = self.health_scores

		r      = requests.post(self.base_url, data=json.dumps(self.data), headers=self.headers)
		result = r.json()

		# Check if keys are properly returned
		self.assertTrue('sentences' in result['result'])
		self.assertTrue('findings'  in result['result'])
		self.assertTrue(isinstance(result['result']['findings']['rheuma'], list))

		self.assertEquals(result['status'], 200)

	def test_empty_valueDescription(self):
		self.data['health_scores'] = self.health_scores
		self.data['health_scores']['rheuma']['values'] = {}

		r      = requests.post(self.base_url, data=json.dumps(self.data), headers=self.headers)
		result = r.json()

		self.assertTrue('sentences' in result['result'])
		self.assertTrue('findings'  in result['result'])
		self.assertTrue(isinstance(result['result']['findings']['rheuma'], list))

		self.assertEquals(result['status'], 200)

	# If nothing is found it should return something
	def test_empty_synonyms(self):
		import copy

		tempData = copy.copy(self.data)
		tempData['health_scores'] = {
			"rheuma" : {
				"synonyms" : []
			}
		}

		r      = requests.post(self.base_url, data=json.dumps(tempData), headers=self.headers)
		result = r.json()

		self.assertTrue('sentences' in result['result'])
		self.assertTrue('findings'  in result['result'])
		self.assertTrue(isinstance(result['result']['findings']['rheuma'], list))
		self.assertEquals(len(result['result']['findings']['rheuma']), 0)

		self.assertEquals(result['status'], 200)
	'''

	def test_unfound_synonyms(self):
		import copy

		tempData = copy.copy(self.data)
		tempData['health_scores'] = {
			"rheuma" : {
				"synonyms" : ["924989ufhusadfhjehrewrwer9ae"]
			}
		}

		r      = requests.post(self.base_url, data=json.dumps(tempData), headers=self.headers)
		result = r.json()

		self.assertTrue('sentences' in result['result'])
		self.assertTrue('findings'  in result['result'])
		self.assertTrue(isinstance(result['result']['findings']['rheuma'], list))
		self.assertEquals(len(result['result']['findings']['rheuma']), 0)

		self.assertEquals(result['status'], 200)


if __name__ == '__main__':
	print "Testing basic API functionality\n"
	suite = unittest.TestLoader().loadTestsFromTestCase(TestBasicAPI)
	unittest.TextTestRunner(verbosity=2).run(suite)
	print "\n\n"

	print "Testing simple text analysis functionality\n"
	suite = unittest.TestLoader().loadTestsFromTestCase(TestSimpleFunctions)
	unittest.TextTestRunner(verbosity=2).run(suite)
	print "\n\n"

	print "Testing result format\n"
	suite = unittest.TestLoader().loadTestsFromTestCase(TestResultFormatting)
	unittest.TextTestRunner(verbosity=2).run(suite)
	print "\n\n"

	print "Testing extraction functionality\n"
	suite = unittest.TestLoader().loadTestsFromTestCase(TestExtractionFunctions)
	unittest.TextTestRunner(verbosity=2).run(suite)
	print "\n\n"

