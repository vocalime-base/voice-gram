from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name

from services.States import States
from services.Utils import createEmptyElicitSlotDirective, createFilledElicitSlotDirective, getChatListElements


class CancelIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type('IntentRequest')(handler_input) and is_intent_name('AMAZON.CancelIntent')(handler_input)

    def handle(self, handler_input):
        sessionAttributes = handler_input.attributes_manager.session_attributes

        if not sessionAttributes['isAuthorized']:
            speech_text = handler_input.i18n.t('Errors.noAccountLinked')
            handler_input.response_builder.speak(speech_text).set_should_end_session(True)

            return handler_input.response_builder.response

        if (sessionAttributes['state'] == States.SEND.value and 'write' in sessionAttributes and 'text' in
                sessionAttributes['write'] and len(sessionAttributes['write']['text']) == 0):
            speech_text = handler_input.i18n.t('SendMessageIntent.elicit.chatName')
            handler_input.response_builder.speak(speech_text).add_directive(
                createEmptyElicitSlotDirective(slotName = 'chatName'))
        elif (sessionAttributes['state'] == States.SEND.value and 'write' in sessionAttributes and 'text' in
              sessionAttributes['write'] and len(
                    sessionAttributes['write']['text']) > 0):
            sessionAttributes['write']['text'] = sessionAttributes['write']['text'][:-1]
            speech_text = handler_input.i18n.t('SendMessageIntent.elicit.text')
            chatId = sessionAttributes['write']['chat']['id']
            chatName = sessionAttributes['write']['chat']['name']
            handler_input.response_builder.speak(speech_text).add_directive(
                createFilledElicitSlotDirective(slotName = 'text', chatName = chatName, chatId = chatId))
        else:
            if 'read' not in sessionAttributes or len(sessionAttributes['read']['chats']) == 0:
                speech_text = handler_input.i18n.t('StopIntent.speech.close')
                handler_input.response_builder.speak(speech_text).set_should_end_session(True)
            else:
                sessionAttributes['state'] = States.READ
                chats = sessionAttributes['read']['chats']
                chatNames, firstChat, lastChat = getChatListElements(chats = chats)
                speech_text = handler_input.i18n.t('ReadMessageIntent.speech.middleRecap',
                                                   count = len(chats),
                                                   chats = chatNames, lastChat = lastChat, fistChat = firstChat)

                handler_input.response_builder.speak(speech_text).ask(speech_text)

        return handler_input.response_builder.response
