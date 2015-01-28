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
		self.data = {"text" : "Example sentences, which can be tokenized. The first agatston score is 612. We can also split the sentences. We can extract scores like an agatston score of 432. Other agatston scores are -9 which is too low. Also, 8,6 for agatston is incorrect. Finally, an agatston score of 40000 is too high to be possible."}
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
					'group' : 0
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
		self.assertTrue('result' in result)

		# assert existence of agatston score in result
		self.assertTrue('agatston' in result['result'])

		# assert correct value of agatston
		self.assertEquals(len(result['result']['agatston']), 2)
		self.assertEquals(result['result']['agatston'][0]['value'], 612)
		self.assertEquals(result['result']['agatston'][1]['value'], 432)


	def test_multiple_values_fuzzy(self):
		self.data['health_scores'] = {
			'agatston' : {
				'synonyms' : [
					'agatston',
					'agatston-score',
					'agatstonscore',
					'kalkscore',
					'calciumscore'
				]
			}
		}
		r = requests.post(self.base_url, data=json.dumps(self.data), headers=self.headers)
		result = r.json()

		# assert status
		self.assertEquals(result['status'], 200)

		#assert existence of json result
		self.assertTrue('result' in result)

		# assert existence of agatston score in result
		self.assertTrue('agatston' in result['result'])

		# assert correct value of agatston
		self.assertEquals(len(result['result']['agatston']), 5)
		self.assertEquals(result['result']['agatston'][0]['value'], "612")
		self.assertEquals(result['result']['agatston'][1]['value'], "432")
		self.assertEquals(result['result']['agatston'][2]['value'], "-9")
		self.assertEquals(result['result']['agatston'][3]['value'], "8,6")
		self.assertEquals(result['result']['agatston'][4]['value'], "40000")


	def test_nonexistent_type(self):
		self.data['health_scores'] = self.health_scores
		self.data['health_scores']['agatston']['values']['type'] = "string"
		r = requests.post(self.base_url, data=json.dumps(self.data), headers=self.headers)
		result = r.json()

		# assert status
		self.assertEquals(result['status'], 400)

	def test_types(self):
		types = ('float','int','long')
		self.data['health_scores'] = self.health_scores

		for t in types:
			self.data['health_scores']['agatston']['values']['type'] = t
			r = requests.post(self.base_url, data=json.dumps(self.data), headers=self.headers)
			result = r.json()

			# assert status
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

	print "Testing extraction functionality\n"
	suite = unittest.TestLoader().loadTestsFromTestCase(TestExtractionFunctions)
	unittest.TextTestRunner(verbosity=2).run(suite)
	print "\n\n"
