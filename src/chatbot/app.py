import json
import logging
from collections import namedtuple

from flask import Flask, make_response, request

from chatbot.dialogflow import Dialogflow
from chatbot.userlike import InvalidInput, UnsupportedMessage, parse_input, format_output

LOG = logging.getLogger(__name__)


Route = namedtuple("Route", ["func", "rule", "options"])


class FlaskRouting(object):
    """ Class for representing Flask application endpoints """

    def __init__(self):
        self.routes = list()

    def route(self, rule, **options):
        """ Decorator for storing routing information """
        def wrapper(func):
            self.routes.append(Route(func, rule, options))
            return func
        return wrapper

    def register_routes(self, route_func_owner, flask_obj):
        """ Add URL rules to the specified Flask object based on values stored via decorator """
        for r in self.routes:
            flask_obj.add_url_rule(r.rule, r.options.pop("endpoint", None),
                                   r.func.__get__(route_func_owner, type(route_func_owner)), **r.options)


router = FlaskRouting()


def _response_ok(data=None):
    """ Create a JSON OK response with HTTP 200 code """
    response = make_response(dict() if not data else json.dumps(data))
    response.headers["Content-Type"] = "application/json"
    response.status_code = 200
    return response


def _response_error(message, details=None, code=500):
    """ Create a JSON error response with specified HTTP code """
    data = {
        "message": message,
        "details": details,
    }
    response = make_response(json.dumps(data))
    response.headers["Content-Type"] = "application/json"
    response.status_code = code
    return response


class ChatbotApp(object):
    """ Class for representing the chatbot Flask application """

    def __init__(self, config):
        self.security_token = config["userlike"]["security_token"]
        self.dialogflow = Dialogflow(
            project=config["dialogflow"]["project"],
            location=config["dialogflow"]["location"],
            agent=config["dialogflow"]["agent"],
            default_language=config["dialogflow"]["default_language"],
        )
        self.app = Flask(__name__)
        router.register_routes(self, self.app)

    @router.route("/", methods=["GET"])
    def status(self):
        """ Simple status endpoint """
        return _response_ok()

    @router.route("/webhook", methods=["POST"])
    def webhook(self):
        """ Userlike webhook endpoint """
        security_token = request.headers.get("SECURITY-TOKEN")
        if not security_token or security_token != self.security_token:
            return _response_error("unauthorized", details="Invalid or missing token", code=403)
        try:
            session_id, input_text = parse_input(request.json)
        except InvalidInput as e:
            return _response_error("invalid input", details=str(e), code=400)
        except UnsupportedMessage as e:
            return _response_error("unsupported message", details=str(e), code=400)
        if not input_text:
            return _response_ok()
        try:
            output_text = self.dialogflow.detect_intent_text(session_id, input_text)
            return _response_ok(format_output(session_id, output_text))
        except Exception as e:
            return _response_error("unknown error", details=str(e), code=500)
