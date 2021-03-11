from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name


class StopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("IntentRequest")(handler_input) and is_intent_name('AMAZON.StopIntent')(handler_input)

    def handle(self, handler_input):
        speech_text = handler_input.i18n.t('StopIntent.speech.close')
        handler_input.response_builder.speak(speech_text).set_should_end_session(True)

        return handler_input.response_builder.response
