#!/usr/bin/env python

"""

Simple web service for the WMD classifier. Examples:

$ curl -X GET http://localhost:8080/pred_text/sarin%20gas
$ curl -i -F data=@test.json http://localhost:8080/pred_file

Note that the model needs to have been pickled with joblib, like so:

    joblib.dump(clf, "exp01.mdl", compress=9)

"""

import json
from urllib2 import unquote
from bottle import route, request, run
from character import Character


def parse_arg(data):
    data = unquote(data)
    if data.startswith('[') or data.startswith('{'):
        data = json.loads(data)
    elif data.isdigit():
        data = int(data)
    return data


@route('/ikgen', method='GET')
def display_character():
    A = {}
    for k, v in request.query.items():
        A.update({k: parse_arg(v)})
    c = Character(**A)
    return "<pre>"+c.summary()+"</pre>"


run(host='192.168.1.135', port=8080, debug=True)
