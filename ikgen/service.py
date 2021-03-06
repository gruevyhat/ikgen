#!/usr/bin/env python

"""

Simple web service for the generator. Example:

$ curl -X GET http://localhost:8080/ikgen

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


def start_service(host='localhost', port='8080'):
    run(host=host, port=port, debug=True)


if __name__ == "__main__":

    start_service('192.168.1.135', 8080)
