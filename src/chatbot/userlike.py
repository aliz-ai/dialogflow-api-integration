import logging
import uuid

LOG = logging.getLogger(__name__)

SESSION_CACHE = {}


class UnsupportedMessage(Exception):
    """ Exception class for representing unsupported messages """

    def __init__(self, msg):
        super(UnsupportedMessage, self).__init__(msg)


class InvalidInput(Exception):
    """ Exception class for representing malformed input """

    def __init__(self, msg):
        super(InvalidInput, self).__init__(msg)


def _fetch_from_input(request, json_path):
    current_node = request
    for path in json_path.split("."):
        if path not in current_node:
            raise InvalidInput(f"Could not fetch: {json_path}")
        current_node = current_node[path]
    return current_node


def _fetch_session_id(cid):
    if cid not in SESSION_CACHE:
        SESSION_CACHE[cid] = uuid.uuid4()
    return SESSION_CACHE[cid]


def _fetch_cid(session_id):
    for cid, sid in SESSION_CACHE.items():
        if sid == session_id:
            return cid
    raise KeyError(session_id)


def parse_input(request):
    """ Parse an incoming webhook payload from Userlike """
    cid = _fetch_from_input(request, "info.cid")
    message_type = _fetch_from_input(request, "packet.name")
    if message_type == "message":
        message = _fetch_from_input(request, "packet.payload.body")
        return _fetch_session_id(cid), message
    elif message_type == "start":
        return _fetch_session_id(cid), None
    else:
        raise UnsupportedMessage(f"Message type not supported: {message_type}")


def format_output(session_id, response):
    """ Format an outgoing payload for Userlike """
    return {
        "info": {
            "cid": _fetch_cid(session_id),
        },
        "packet": {
            "name": "message",
            "payload": {
                "body": response
            }
        }
    }
