from pprint import pprint
import json

from six import string_types
from flask import Flask
from flask.json import jsonify
from flask import request
from flask import make_response

from exoline import exo
from exoline import __version__ as version

app = Flask(__name__)
app.debug = True

@app.route('/')
def hello():
    return '''<html><body><div>Welcome to Exon, a web service for <a href="https://github.com/exosite/exoline">Exoline</a>, which is a command line tool for a <a href="https://exosite.com">web service</a>. Check out this code, which creates a 1 hour temporary device, sets it up with a temperature conversion script, and does a conversion.</div>

       <pre>
       $ TEMPCIK=`curl cik.herokuapp.com`
       $ alias exon='curl exon.herokuapp.com/api '
       $ exon -d '{"args": ["spec", "'$TEMPCIK'", "http://tinyurl.com/exospec-tempconvert", "--create"]}'
       $ exon -d '{"args": ["write", "'$TEMPCIK'", "temp_c", "--value=32"]}'
       $ exon -d '{"args": ["update", "'$TEMPCIK'", "temp_f", "-"], "stdin": "{\"name\": \"This is the temperature in Fahrenheit\"}"}'
       $ exon -d '{"args": ["twee", "'$TEMPCIK'"]}' | jq .stdout -r
       </pre>

       <div>Implementing a command line tool for accessing Exon is left as an exercise for the reader. :-)</div>

       <div>Now serving <a href="https://pypi.python.org/pypi/exoline/''' + version + '">Exoline ' + version + '''</a></div>
       </body></html>'''

@app.route('/api', methods=['POST'])
def api():
    body = request.get_json(force=True)
    if ('args' not in body or type(body['args']) is not list or
            any([not isinstance(a, string_types) for a in body['args']])):
        return make_response('missing or bad args', 400)
    stdin=None
    if 'stdin' in body:
        if type(body(stdin)) is str:
            stdin = body
        else:
            return make_response('stdin must be a string', 400)

    args = ['exo'] + request.get_json(force=True)['args']
    result = exo.run(args)
    return jsonify({
        "exitcode": result.exitcode,
        "stdout": result.stdout,
        "stderr": result.stderr
    })
