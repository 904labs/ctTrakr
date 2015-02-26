import argparse
import json
import logging

from flask import Flask, Response, request, jsonify
from flask.ext.cors import CORS

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from util import errors

#logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'

CORS(app, resources={r"/api/*" : {"origins" : "*"}})

@app.errorhandler(errors.CustomAPIError)
def handle_invalid_usage(error):
	response = error.to_dict()
	return response


@app.route('/api/<tasktype>/<taskname>', methods=['GET'])
def run_task_get(tasktype, taskname):
	raise errors.CustomAPIError('Method not allowed', status_code=405, payload={'method':'GET'})


@app.route('/api/<tasktype>/<taskname>', methods=['POST'])
def run_task(tasktype, taskname):
	"""Run named task on a document fed as POST data.
	The POST data should have Content-type application/json.
	"""

	try:
		tasktype = str(tasktype)
		taskname = str(taskname)

		nlp  = getattr(__import__("nlp", fromlist=[tasktype]), tasktype)
		func = getattr(nlp, taskname)
	except AttributeError:
		raise errors.CustomAPIError('Cannot locate endpoint', status_code=404, payload={'endpoint':'api/%s/%s'%(tasktype,taskname)})
	else:
		content_type = request.headers['Content-Type']

		if content_type == 'application/json':
			kwargs = request.get_json()
			result = func(**kwargs)
			return jsonify(result=result, status=200)

		raise errors.CustomAPIError('Unsupported content-type', status_code=415, payload={'content-type':content_type})

@app.route('/<path:path>', methods=['GET','POST'])
def catchall(path):
	raise errors.CustomAPIError('Cannot locate endpoint', status_code=404, payload={'endpoint':path})


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="ctTrakr web server")
	parser.add_argument('--host', dest='host', default='127.0.0.1',
						help='Host to listen on.')
	parser.add_argument('--port', dest='port', default=5000, type=int,
						help='Port to listen on.')
	parser.add_argument('--threads', dest='threads', default=1, type=int,
						help='Number of threads.')
	args = parser.parse_args()

	http_server = HTTPServer(WSGIContainer(app))
	http_server.bind(args.port, address=args.host)
	http_server.start(args.threads)
	IOLoop.instance().start()
