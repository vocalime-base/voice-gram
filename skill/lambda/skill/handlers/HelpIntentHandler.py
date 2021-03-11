from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name


class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("IntentRequest")(handler_input) and is_intent_name('AMAZON.HelpIntent')(handler_input)

    def handle(self, handler_input):
        sessionAttributes = handler_input.attributes_manager.session_attributes

        if not sessionAttributes['isAuthorized']:
            speech_text = handler_input.i18n.t('Errors.noAccountLinked')
            handler_input.response_builder.speak(speech_text).set_should_end_session(True)
        else:
            speech_text = handler_input.i18n.t('HelpIntent.speech.authorized')
            handler_input.response_builder.speak(speech_text).ask(speech_text)

        return handler_input.response_builder.response
