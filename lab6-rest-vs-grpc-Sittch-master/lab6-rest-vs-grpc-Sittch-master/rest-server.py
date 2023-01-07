from flask import Flask, request, Response
import jsonpickle
from PIL import Image
import base64
import io

# Initialize the Flask application
app = Flask(__name__)

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)

@app.route('/api/add/<int:a>/<int:b>', methods=['GET', 'POST'])
def add(a,b):
    response = {'sum' : str( a + b)}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

# route http posts to this method
@app.route('/api/rawimage', methods=['POST'])
def rawimage():
    r = request
    # convert the data to a PIL image type so we can extract dimensions
    try:
        ioBuffer = io.BytesIO(r.data)
        img = Image.open(ioBuffer)
    # build a response dict to send back to client
        response = {
            'width' : img.size[0],
            'height' : img.size[1]
            }
    except:
        response = { 'width' : 0, 'height' : 0}
    # encode response using jsonpickle
    response_pickled = jsonpickle.encode(response)

    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/api/dotproduct', methods=['POST'])
def dotproduct():
    r = request
    try:
        json = jsonpickle.decode(r.data)
        c = 0
        for a,b in zip(json['a'],json['b']):
            c += a*b
        response = {'dotproduct' : str( c )}
    except:
        response = {'dotproduct' : 'Something Wrong!'}
    # encode response using jsonpickle
    response_pickled = jsonpickle.encode(response)

    return Response(response=response_pickled, status=200, mimetype="application/json")

# route http posts to this method
@app.route('/api/jsonimage', methods=['POST'])
def jsonimage():
    r = request
    try:
        json = jsonpickle.decode(r.data)
        img  = Image.open(io.BytesIO(base64.b64decode(json['img'].encode())))
        response = {
            'width' : img.size[0],
            'height' : img.size[1]
            }
    except:
        response = { 'width' : 0, 'height' : 0}
    # encode response using jsonpickle
    response_pickled = jsonpickle.encode(response)

    return Response(response=response_pickled, status=200, mimetype="application/json")

# start flask app
app.run(host="0.0.0.0", port=5000)