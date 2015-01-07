# -*- coding: utf-8 -*-

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
    return '''<html><body><div>Welcome to Exon, a web service for <a href="https://github.com/exosite/exoline">Exoline</a>. Exon lets you run Exoline commands without installing Exoline. Here's an example that creates a 1 hour temporary device, sets it up with a temperature conversion script, and does a conversion.</div>

<pre>
$ <strong>TEMPCIK=`curl --silent cik.herokuapp.com`</strong>
$ <strong>alias exon='curl --silent exon.herokuapp.com/api '</strong>
$ <strong>exon -d '{"args": ["spec", "'$TEMPCIK'", "http://tinyurl.com/exospec-tempconvert", "--create"]}'</strong>
{
  "exitcode": 0,
  "stderr": "",
  "stdout": "Running spec on: 23713c7a99d613c85e280d5f0126acda62624c0b\ntemp_f not found.\nCreating dataport with name: temp_f, alias: temp_f, format: float\ntemp_c not found.\nCreating dataport with name: temp_c, alias: temp_c, format: float\nconvert.lua not found.\nNew script RID: 2996e4b25b80b08d233a9f8622447a78f87bef6c\nAliased script to: convert.lua"
}
$ <strong>exon -d '{"args": ["write", "'$TEMPCIK'", "temp_c", "--value=32"]}'</strong>
{
  "exitcode": 0,
  "stderr": "",
  "stdout": ""
}
$ <strong>exon -d '{"args": ["update", "'$TEMPCIK'", "temp_f", "-"], "stdin": "{\\"name\\": \\"This is the temperature in Fahrenheit\\"}"}'</strong>
{
  "exitcode": 0,
  "stderr": "",
  "stdout": "ok"
}
$ <strong>exon -d '{"args": ["twee", "'$TEMPCIK'"]}' | jq .stdout -r</strong>
Temporary CIK    cl cik: 23713c7a99d613c85e280d5f0126acda62624c0b
  ├─temp_c                                 dp.f temp_c: 32.0 (just now)
  ├─This is the temperature in Fahrenheit  dp.f temp_f: 89.6 (just now)
  └─convert.lua                            dr.s convert.lua: line 9: Converted 32.000000C to 89.600000F (just now)
</pre>

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
        if isinstance(body['stdin'], string_types):
            stdin = body['stdin']
        else:
            return make_response('stdin must be a string', 400)

    args = ['exo'] + body['args']
    result = exo.run(args, stdin=stdin)
    return jsonify({
        "exitcode": result.exitcode,
        "stdout": result.stdout,
        "stderr": result.stderr
    })
