import requests

from flask import Flask, Response, jsonify
from flask import request as flask_request

from ddtrace import tracer, patch
from ddtrace.contrib.flask import TraceMiddleware


# Tracer configuration
tracer.configure(hostname='agent')
patch(requests=True)

app = Flask('api')
traced_app = TraceMiddleware(app, tracer, service='thinker-api')


@app.route('/think/')
def think_handler():
    # TODO: make this use config.requests['distributed_tracing'] = True instead
    thoughts = requests.get('http://thinker:5001/', headers={
        'x-datadog-trace-id': str(tracer.current_span().trace_id),
        'x-datadog-parent-id': str(tracer.current_span().span_id),
    }, params={
        'subject': flask_request.args.getlist('subject', str),
    }).content
    return Response(thoughts, mimetype='application/json')
