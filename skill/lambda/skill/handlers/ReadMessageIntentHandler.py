from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model.dialog import DynamicEntitiesDirective
from ask_sdk_model.er.dynamic import UpdateBehavior

from services.States import States
from services.Utils import getChatName, createChatNameDynamicEntities


class ReadMessageIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type('IntentRequest')(handler_input) and is_intent_name('ReadMessageIntent')(handler_input)

    def handle(self, handler_input):
        sessionAttributes = handler_input.attributes_manager.session_attributes
        requestAttributes = handler_input.attributes_manager.request_attributes

        if not sessionAttributes['isAuthorized']:
            speech_text = handler_input.i18n.t('Errors.noAccountLinked')
            handler_input.response_builder.speak(speech_text).set_should_end_session(True)
        else:
            client = requestAttributes['tg']

            chats, unreadCount = client.getUnreadChats()

            if chats:
                sessionAttributes['state'] = States.READ
                sessionAttributes['read'] = {'chats': chats, 'unreadCount': unreadCount}
                names = list(map(lambda chat: getChatName(chat), chats))
                comma = ', '
                chatNames = comma.join(names[:-1])
                firstChat = names[0]
                lastChat = names[-1]
                speech_text = handler_input.i18n.t('ReadMessageIntent.speech.middleRecap', count = len(chats),
                                                   unreadMessages = unreadCount, chats = chatNames, lastChat = lastChat,
                                                   firstChat = firstChat)

                handler_input.response_builder.speak(speech_text).ask(speech_text)
            else:
                sessionAttributes['state'] = States.SEND
                speech_text = handler_input.i18n.t('ReadMessageIntent.speech.middleRecap', count = 0)
                handler_input.response_builder.speak(speech_text).ask(speech_text)

            handler_input.response_builder.add_directive(
                DynamicEntitiesDirective(update_behavior = UpdateBehavior.REPLACE,
                                         types = createChatNameDynamicEntities(client)))

        return handler_input.response_builder.response
