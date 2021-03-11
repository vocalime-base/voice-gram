import os
import json

from ask_sdk_core.dispatch_components import AbstractExceptionHandler, AbstractRequestHandler
from ask_sdk_core.utils import is_request_type
from ask_sdk_model.dialog.dynamic_entities_directive import DynamicEntitiesDirective
from ask_sdk_model.er.dynamic.update_behavior import UpdateBehavior


class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        handler_input.response_builder.add_directive(
            DynamicEntitiesDirective(update_behavior = UpdateBehavior.CLEAR)).set_should_end_session(True)

        return handler_input.response_builder.response


class ErrorHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, error):
        print(json.dumps({
            'error': True,
            'message': str(error)
        }))

        try:
            print(json.dumps(handler_input.request_envelope.to_dict()))
        except TypeError:
            print(handler_input.request_envelope)

        speech_text = handler_input.i18n.t('FallbackIntent.speech.text')
        handler_input.response_builder.speak(speech_text).ask(speech_text)

        return handler_input.response_builder.response
