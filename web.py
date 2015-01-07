from pprint import pprint
import json

from flask import Flask
from flask.json import jsonify
from flask import request

from exoline import exo

app = Flask(__name__)
app.debug = True

@app.route('/')
def hello():
    return '''<html><body>Welcome to Exonline, the web site for a command line for a web site. Try this:
       <pre>
       $ curl exonline.herokuapp.com/api -d '{"args": ["tree", "CIK-HERE"]}'
       </pre>
       </body></html>'''

@app.route('/api', methods=['POST'])
def api():
    args = ['exo'] + request.get_json(force=True)['args']
    result = exo.run(args)
    return jsonify({
        "exitcode": result.exitcode,
        "stdout": result.stdout,
        "stderr": result.stderr
    })
