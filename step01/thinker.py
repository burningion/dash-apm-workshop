import asyncio
import logging

from aiohttp import web

from ddtrace import tracer
from ddtrace.contrib.aiohttp import trace_app

from thoughts import thoughts


# Logger configuration
logger = logging.getLogger(__name__)


# Tracer configuration
tracer.configure(hostname='agent')


@tracer.wrap(name='think')
async def think(subject):
    tracer.current_span().set_tag('subject', subject)

    await asyncio.sleep(0.5)
    return thoughts[subject]


async def handle(request):
    response = {}
    for subject in request.query.getall('subject', []):
        try:
            thought = await think(subject)
            response[subject] = {
                'error': False,
                'quote': thought.quote,
                'author': thought.author,
            }
        except KeyError:
            response[subject] = {
                'error': True,
                'reason': 'This subject is too complicated to be resumed in one sentence.'
            }

    return web.json_response(response)


app = web.Application()
app.router.add_get('/', handle)


# Setup access logging
aiohttp_logger = logging.getLogger('aiohttp.access')
aiohttp_logger.setLevel(logging.DEBUG)
aiohttp_logger.addHandler(logging.StreamHandler())


trace_app(app, tracer, service='thinker-microservice')
app['datadog_trace']['distributed_tracing_enabled'] = True
web.run_app(app, port=8000)
