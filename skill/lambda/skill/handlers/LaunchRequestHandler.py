from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type
from ask_sdk_model.dialog.dynamic_entities_directive import DynamicEntitiesDirective
from ask_sdk_model.er.dynamic.update_behavior import UpdateBehavior

from services.States import States
from services.Utils import createChatNameDynamicEntities, getChatListElements


class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        sessionAttributes = handler_input.attributes_manager.session_attributes
        requestAttributes = handler_input.attributes_manager.request_attributes

        if not sessionAttributes['isAuthorized']:
            speech_text = handler_input.i18n.t('Errors.noAccountLinked')
            handler_input.response_builder.speak(speech_text).set_should_end_session(True)
        else:
            client = requestAttributes['tg']

            chats, unreadCount = client.getUnreadChats()

            name = client.getFirstName()

            if chats:
                sessionAttributes['state'] = States.READ
                sessionAttributes['read'] = {'chats': chats, 'unreadCount': unreadCount}
                chatNames, firstChat, lastChat = getChatListElements(chats = chats)
                speech_text = handler_input.i18n.t('ReadMessageIntent.speech.recap', count = len(chats),
                                                   unreadMessages = unreadCount, chats = chatNames, lastChat = lastChat,
                                                   firstChat = firstChat, name = name)

                handler_input.response_builder.speak(speech_text).ask(speech_text)
            else:
                sessionAttributes['state'] = States.SEND
                speech_text = handler_input.i18n.t('LaunchRequest.speech.sendMessage', name = name)
                handler_input.response_builder.speak(speech_text).ask(speech_text)

            handler_input.response_builder.add_directive(
                DynamicEntitiesDirective(update_behavior = UpdateBehavior.REPLACE,
                                         types = createChatNameDynamicEntities(client)))

        return handler_input.response_builder.response
