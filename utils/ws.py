from flask import Flask, jsonify, request, Response

from utils.config import get_config
from utils.log import get_logger
from functools import wraps
import graphene
from flask_graphql import GraphQLView


app = Flask(__name__)
logger = get_logger(__name__)


def check_auth(username, password):
    return username == get_config()['ws']['username'] and password == get_config()['ws']['password']


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


ws_registrator = {}


class Ws:
    def __init__(self, servicename):
        self.name = servicename

    def request_with_body(self, body):
        pass

    def request_no_body(self):
        pass


def register_service(service: Ws):
    if not(ws_registrator.get(service.name) is None):
        logger.error(
            "Service [%s] cannot be registered because there is already a service with the same name")
    else:
        logger.info('Registering ws [%s]' % (service.name))
        ws_registrator[service.name] = service


def call_service(service: Ws, body=None):
    if (service == 'service_list'):
        result = []
        for service in ws_registrator:
            result.append(ws_registrator.get(service).name)
        return result
    ws = ws_registrator.get(service)
    if not(body is None):
        return ws.request_with_body(body)
    else:
        return ws.request_no_body()


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def all(path):
    return jsonify({
        'data': 'Method GET not supported on /{0}'.format(path),
        'status': 'error'
    })


@app.route('/v1/<service>', methods=['POST'])
def service(service):
    content = request.get_json()
    logger.debug('Request [{0}] - body {1}'.format(service, content))
    try:
        response = call_service(service, content)
        result = {
            'data': response,
            'status': 'ok'
        }
    except Exception as e:
        result = {
            'data': str(e),
            'status': 'error'
        }
        logger.error('Response returned an error')

    logger.debug('Response [{0}] - body {1}'.format(service, result))
    return jsonify(result)


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logger.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500


@app.errorhandler(404)
def not_found(e):
    # Log the error and stacktrace.
    logger.exception('An error occurred during a request.')
    return 'An internal error occurred.', 404


def run(query=None, mutation=None):
    port = get_config()['ws']['port']
    logger.info("Starting webservices on port [%s]" % (port))
    if not(query is None):
        schema = graphene.Schema(query=query, mutation=mutation)
        app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql',
                                                                   schema=schema, graphiql=True))
    app.run(port=port)
