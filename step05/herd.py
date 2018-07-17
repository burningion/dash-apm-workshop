import requests

from flask import Flask, Response, jsonify

app = Flask('humanherd')

@app.route('/')
def hello():
    return 'This container will generate loads of traffic to populate trace search.'
