# -*- coding: utf-8 -*-
import os

from six import string_types
from flask import Flask
from flask.json import jsonify
from flask import request
from flask import make_response
from flask import render_template
from flask_sslify import SSLify
from exoline import exo
from exoline import __version__ as version

app = Flask(__name__)
app.debug = True # if os.environ.get('DEBUG', False) == 'True' else False
sslify = SSLify(app)

@app.route('/')
def hello():
    return render_template('index.html', version=version)

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
