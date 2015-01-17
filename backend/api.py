from flask import Flask
from flask.ext.restful import reqparse, abort, Api, Resource
from flask.ext.cors import CORS

# from controllers.tokenizeController import Tokenize
from controllers.processController import ProcessText

app = Flask(__name__)
CORS(app, resources=r'/*', allow_headers='Content-Type')
api = Api(app)

# api.add_resource(Tokenize, '/processText')
api.add_resource(ProcessText, '/processText')

if __name__ == '__main__':
  app.run(debug=True)