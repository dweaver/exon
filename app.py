# -*- coding: utf-8 -*-
import os
import json
import re
import csv
import StringIO

from six import string_types
from flask import Flask
from flask.json import jsonify
from flask import request
from flask import make_response
from flask import render_template
from flask_sslify import SSLify
from flask.ext.cors import CORS
import requests
from exoline import exo
from exoline import __version__ as version

app = Flask(__name__)
app.debug = True # if os.environ.get('DEBUG', False) == 'True' else False
sslify = SSLify(app)
CORS(app)

@app.route('/')
def hello():
    return render_template('index.html', version=version)

@app.route('/repl')
def repl():
    r = requests.get('http://cik.herokuapp.com')
    tempcik = None
    if r.status_code == 200:
        tempcik = r.text
    return render_template('repl.html', version=version, tempcik=tempcik)

def check(result):
    """Check an Exoline result, and print debug output on error."""
    if result.exitcode != 0:
        raise Exception(json.dumps({
            'stderr': result.stderr,
            'stdout': result.stdout,
            'exitcode': result.exitcode
        }))


@app.route('/api/examples/2.json')
def example2():
    return jsonify({
        "tree": {
    "name": "flare",
    "children": [
    {
    "name": "analytics",
    "children": [
        {"name": "another"}
        ]
    }
    ]
    }})

@app.route('/api/examples/1.json')
def example1():
    res = requests.get('http://cik.herokuapp.com/api/create?vendor')
    tempcik = None
    if res.status_code == 200:
        details = res.json()
        tempcik = details['cik']
        r = exo.run(['exo', 'create', tempcik,
            '--type=client', '--ridonly', '--name=A'])
        check(r)
        rid2 = r.stdout
        r = exo.run(
            ['exo', 'create', tempcik + ':c' + rid2,
                '--type=dataport', '--ridonly', '--format=float',
                '--name=B', '--alias=humidity'])
        rid3 = r.stdout
        r = exo.run(
            ['exo', 'record', tempcik + ':c' + rid2, rid3,
                '--value=1000000,3.1', '--value=2000000,2.1', '--value=3000000,1.1'])
        check(r)
        r = exo.run(
            ['exo', 'read', tempcik + ':c' + rid2, rid3, '--limit=4', '--timeformat=unix'])
        check(r)
        reader = csv.reader(StringIO.StringIO(r.stdout))
        points = []
        for row in reader:
            points.append(row)
        r = exo.run([
            'exo',
            'info',
            tempcik, '--include=basic,description,key', '--recursive'])
        check(r)
        tree = json.loads(r.stdout)

        ## Make the tree look the way we want
        # move children out of info
        tree['children'] = tree['info']['children']
        del(tree['info']['children'])
        tree['children'][0]['children'] = tree['children'][0]['info']['children']
        del(tree['children'][0]['info']['children'])
        # inject the points
        tree['children'][0]['children'][0]['points'] = points
        #
        return jsonify({
            'cikfountain': details,
            'tree': tree
        })
    return make_response('failed to make example', 400)


@app.route('/examples')
def examples():
    return render_template('examples.html', version=version)


@app.route('/api', methods=['POST'])
def api():
    body = request.get_json(force=True)
    if ('args' not in body or type(body['args']) is not list or
            any([not isinstance(a, string_types) for a in body['args']])):
        return make_response('missing or bad args', 400)
    stdin = None
    if 'stdin' in body:
        if isinstance(body['stdin'], string_types):
            stdin = body['stdin']
        else:
            return make_response('stdin must be a string', 400)

    if len(body) > 0 and body['args'][0] == 'exo':
        args = body['args']
    else:
        args = ['exo'] + body['args']
    result = exo.run(args, stdin=stdin)
    return jsonify({
        'exitcode': result.exitcode,
        'stdout': result.stdout,
        'stderr': result.stderr
    })
