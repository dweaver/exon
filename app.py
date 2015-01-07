# -*- coding: utf-8 -*-
import os

from six import string_types
from flask import Flask
from flask.json import jsonify
from flask import request
from flask import make_response
from flask_sslify import SSLify
from exoline import exo
from exoline import __version__ as version

app = Flask(__name__)
app.debug = os.environ.get('DEBUG', False)
sslify = SSLify(app)

@app.route('/')
def hello():
    return '''<html><body>
<h1>Exon</h1>
<div style="width: 60%">Exon is a web service for <a href="https://github.com/exosite/exoline">Exoline</a>. Use Exon to run Exoline commands when you don't have Exoline installed. Here's an example that creates a 1 hour temporary device, uses the Exoline spec command to create two dataports and a temperature conversion <a href="http://docs.exosite.com/scripting">Lua script</a>, and does a conversion.</div>

<pre>
$ <strong>TEMPCIK=`curl --silent cik.herokuapp.com`</strong>
$ <strong>alias exon='curl --silent https://exon.herokuapp.com/api '</strong>
$ <strong>exon -d '{"args": ["spec", "'$TEMPCIK'", "http://tinyurl.com/exospec-tempconvert", "--create"]}'</strong>
{
  "exitcode": 0,
  "stderr": "",
  "stdout": "Running spec on: 23713c7a99d613c85e280d5f0126acda62624c0b\\ntemp_f not found.\\nCreating dataport with name: temp_f, alias: temp_f, format: float\\ntemp_c not found.\\nCreating dataport with name: temp_c, alias: temp_c, format: float\\nconvert.lua not found.\\nNew script RID: 2996e4b25b80b08d233a9f8622447a78f87bef6c\\nAliased script to: convert.lua"
}
$ <strong>exon -d '{"args": ["write", "'$TEMPCIK'", "temp_c", "--value=0"]}'</strong>
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
$ <strong>exon -d '{"args": ["read", "'$TEMPCIK'", "temp_f"]}'</strong>
{
  "exitcode": 0,
  "stderr": "",
  "stdout": "2015-01-07 11:44:23-06:00,32.0"
}
$ <strong>exon -d '{"args": ["twee", "'$TEMPCIK'"]}' | jq .stdout -r</strong>
Temporary CIK    cl cik: 23713c7a99d613c85e280d5f0126acda62624c0b
  ├─temp_c                                 dp.f temp_c: 0.0 (just now)
  ├─This is the temperature in Fahrenheit  dp.f temp_f: 32.0 (just now)
  └─convert.lua                            dr.s convert.lua: line 9: Converted 0.000000C to 0.000000F (just now)
</pre>

<div>Now serving <a href="https://pypi.python.org/pypi/exoline/''' + version + '">Exoline ' + version + '''</a>
<a href="https://github.com/dweaver/exon"><img style="position: absolute; top: 0; right: 0; border: 0;" src="https://camo.githubusercontent.com/38ef81f8aca64bb9a64448d0d70f1308ef5341ab/68747470733a2f2f73332e616d617a6f6e6177732e636f6d2f6769746875622f726962626f6e732f666f726b6d655f72696768745f6461726b626c75655f3132313632312e706e67" alt="Fork me on GitHub" data-canonical-src="https://s3.amazonaws.com/github/ribbons/forkme_right_darkblue_121621.png"></img>a>
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
