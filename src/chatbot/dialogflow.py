import logging

from google.cloud.dialogflowcx import SessionsClient, TextInput, QueryInput, DetectIntentRequest

LOG = logging.getLogger(__name__)


class Dialogflow(object):
    """ Class implementing Google Dialogflow CX integration """

    def __init__(self, project, location, agent, default_language):
        self.project = project
        self.location = location
        self.agent = agent
        self.default_language = default_language

    def detect_intent_text(self, session_id, text, language=None):
        """ Send the specified text to the agent for processing

        Session ID should be retained so conversation state can be perserved.
        """
        language = language or self.default_language
        client_options = None
        if self.location != "global":
            client_options = {
                "api_endpoint": f"{self.location}-dialogflow.googleapis.com:443"
            }
        query_input = QueryInput(text=TextInput(text=text), language_code=language)
        request = DetectIntentRequest(
            session=f"projects/{self.project}/locations/{self.location}/agents/{self.agent}/sessions/{session_id}",
            query_input=query_input
        )
        response = SessionsClient(client_options=client_options).detect_intent(request=request)

        return "".join([
            "".join(msg.text.text) for msg in response.query_result.response_messages
        ])
