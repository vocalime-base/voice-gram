from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model.ui.link_account_card import LinkAccountCard

from services.States import States
from services.Utils import getChatName, formatMessages


class RepeatIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("IntentRequest")(handler_input) and is_intent_name('AMAZON.RepeatIntent')(handler_input)

    def handle(self, handler_input):
        sessionAttributes = handler_input.attributes_manager.session_attributes

        if not sessionAttributes['isAuthorized']:
            speech_text = handler_input.i18n.t('Errors.noAccountLinked')
            handler_input.response_builder.speak(speech_text).set_should_end_session(True)
        elif 'read' in sessionAttributes and 'current' in sessionAttributes['read']:
            chats = sessionAttributes['read']['chats']
            currentChat = sessionAttributes['read']['current']
            messages = currentChat.get('messages')
            unread = len(messages)

            speech_text = handler_input.i18n.t('ReadMessageIntent.speech.chat',
                                               count = unread,
                                               messages = formatMessages(chat = currentChat, i18n = handler_input.i18n))

            if currentChat.get('canReply'):
                canReply = handler_input.i18n.t('ReadMessageIntent.speech.canReply')
                sessionAttributes['state'] = States.REPLY
            else:
                canReply = ''  # handler_input.i18n.t('ReadMessageIntent.speech.cantReply')
                if len(chats) > 0:
                    names = list(map(lambda chat: getChatName(chat), chats))
                    comma = ', '
                    chatNames = comma.join(names[:-1])
                    fistChat = names[0]
                    lastChat = names[-1]
                    canReply = canReply + handler_input.i18n.t('ReadMessageIntent.speech.middleRecap',
                                                               count = len(chats),
                                                               chats = chatNames, lastChat = lastChat,
                                                               fistChat = fistChat)
                else:
                    sessionAttributes['state'] = States.SEND
                    canReply = canReply + handler_input.i18n.t('ReadMessageIntent.speech.middleRecap', count = 0)

            speech_text = speech_text + canReply

            handler_input.response_builder.speak(speech_text).ask(speech_text)

        else:
            speech_text = handler_input.i18n.t('RepeatIntent.speech.noMessage')
            handler_input.response_builder.speak(speech_text).ask(speech_text)

        return handler_input.response_builder.response
