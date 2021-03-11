from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name

from services.States import States
from services.Utils import createEmptyElicitSlotDirective


class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("IntentRequest")(handler_input) and is_intent_name('AMAZON.FallbackIntent')(
            handler_input)

    def handle(self, handler_input):
        sessionAttributes = handler_input.attributes_manager.session_attributes

        if sessionAttributes.get('state', None) == States.SEND.value:
            speech_text = handler_input.i18n.t('SendMessageIntent.elicit.repeatChatName')
            handler_input.response_builder.speak(speech_text).add_directive(
                createEmptyElicitSlotDirective(slotName = 'chatName'))
        else:
            speech_text = handler_input.i18n.t('FallbackIntent.speech.text')
            handler_input.response_builder.speak(speech_text).ask(speech_text)

        return handler_input.response_builder.response
