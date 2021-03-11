from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name

from services.States import States
from services.Utils import (getChatName, formatMessages, createFilledElicitSlotDirective,
                            createEmptyElicitSlotDirective,
                            getChatListElements)


class YesIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("IntentRequest")(handler_input) and is_intent_name('AMAZON.YesIntent')(handler_input)

    def handle(self, handler_input):
        sessionAttributes = handler_input.attributes_manager.session_attributes
        requestAttributes = handler_input.attributes_manager.request_attributes

        if not sessionAttributes['isAuthorized']:
            speech_text = handler_input.i18n.t('Errors.noAccountLinked')
            handler_input.response_builder.speak(speech_text).set_should_end_session(True)

        # Non ci sono messaggi da leggere e l'utente vuole inviare un messaggio
        if sessionAttributes['state'] == States.SEND.value:
            if 'write' in sessionAttributes and 'text' in sessionAttributes['write']:
                speech_text = handler_input.i18n.t('SendMessageIntent.elicit.unexpected')
                chatId = sessionAttributes['write']['chat']['id']
                chatName = sessionAttributes['write']['chat']['name']
                handler_input.response_builder.speak(
                    speech_text).ask(speech_text).add_directive(
                    createFilledElicitSlotDirective(slotName = 'action', chatId = chatId, chatName = chatName))
            else:
                sessionAttributes['write'] = {'text': []}
                speech_text = handler_input.i18n.t('SendMessageIntent.elicit.chatName')
                handler_input.response_builder.speak(speech_text).add_directive(
                    createEmptyElicitSlotDirective(slotName = 'chatName'))

        # L'utente vuole scrivere un altro messaggio alla stessa persona oppure vuole rispondere ad una persona
        elif sessionAttributes['state'] == States.SEND_AGAIN.value or sessionAttributes['state'] == States.REPLY.value:
            if sessionAttributes['state'] == States.SEND_AGAIN.value:
                chatId = sessionAttributes['write']['chat']['id']
                chatName = sessionAttributes['write']['chat']['name']
            else:
                chatId = sessionAttributes['read']['current']['id']
                chatName = getChatName(sessionAttributes['read']['current'])
                sessionAttributes['write'] = {'chat': {'id': chatId, 'name': chatName}}

            sessionAttributes['state'] = States.SEND
            sessionAttributes['write']['text'] = []

            speech_text = handler_input.i18n.t('SendMessageIntent.elicit.text')
            handler_input.response_builder.speak(speech_text).add_directive(
                createFilledElicitSlotDirective(slotName = 'text', chatId = chatId, chatName = chatName))

        elif sessionAttributes['state'] == States.READ.value:
            chats = sessionAttributes['read']['chats']

            chat = chats[0]
            del chats[0]
            sessionAttributes['read']['chats'] = chats
            sessionAttributes['read']['current'] = chat
            unread = chat.get('unreadCount')
            messages = requestAttributes['tg'].getMessages(chatId = chat['id'], limit = unread)
            chat['messages'] = messages

            speech_text = handler_input.i18n.t('ReadMessageIntent.speech.chat',
                                               count = unread,
                                               limit = handler_input.i18n.t(
                                                   'ReadMessageIntent.speech.limit') if unread > 10 else '',
                                               messages = formatMessages(chat = chat, i18n = handler_input.i18n))

            if chat.get('canReply'):
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

        return handler_input.response_builder.response


class NoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("IntentRequest")(handler_input) and is_intent_name('AMAZON.NoIntent')(handler_input)

    def handle(self, handler_input):
        sessionAttributes = handler_input.attributes_manager.session_attributes

        if not sessionAttributes['isAuthorized']:
            speech_text = handler_input.i18n.t('Errors.noAccountLinked')
            handler_input.response_builder.speak(speech_text).set_should_end_session(True)

        if sessionAttributes['state'] == States.SEND.value:
            if 'write' in sessionAttributes and 'text' in sessionAttributes['write']:
                speech_text = handler_input.i18n.t('SendMessageIntent.elicit.unexpected')
                chatId = sessionAttributes['write']['chat']['id']
                chatName = sessionAttributes['write']['chat']['name']
                handler_input.response_builder.speak(
                    speech_text).ask(speech_text).add_directive(
                    createFilledElicitSlotDirective(slotName = 'action', chatId = chatId, chatName = chatName))
            else:
                speech_text = handler_input.i18n.t('StopIntent.speech.close')
                handler_input.response_builder.speak(speech_text).set_should_end_session(True)
        elif sessionAttributes['state'] == States.SEND_AGAIN.value or sessionAttributes['state'] == States.REPLY.value:
            if 'read' not in sessionAttributes or len(sessionAttributes['read']['chats']) == 0:
                if 'write' in sessionAttributes and len(sessionAttributes['write']['text']) > 0:
                    sessionAttributes['state'] = States.SEND
                    sessionAttributes['write'].pop('text')
                    speech_text = handler_input.i18n.t('SendMessageIntent.speech.sendAnotherMessage')
                    handler_input.response_builder.speak(speech_text).ask(speech_text)
                else:
                    sessionAttributes['state'] = States.SEND
                    speech_text = handler_input.i18n.t('ReadMessageIntent.speech.middleRecap', count = 0)
                    handler_input.response_builder.speak(speech_text).ask(speech_text)
            else:
                sessionAttributes['state'] = States.READ
                names = list(map(lambda chat: getChatName(chat), sessionAttributes['read']['chats']))
                comma = ', '
                chatNames = comma.join(names[:-1])
                fistChat = names[0]
                lastChat = names[-1]
                speech_text = handler_input.i18n.t('ReadMessageIntent.speech.middleRecap',
                                                   count = len(sessionAttributes['read']['chats']),
                                                   chats = chatNames, lastChat = lastChat, fistChat = fistChat)

                handler_input.response_builder.speak(speech_text).ask(speech_text)
        elif sessionAttributes['state'] == States.READ.value:
            chats = sessionAttributes['read']['chats']
            if len(chats) > 1:
                del chats[0]
                sessionAttributes['read']['chats'] = chats
                chatNames, firstChat, lastChat = getChatListElements(chats = chats)
                speech_text = handler_input.i18n.t('ReadMessageIntent.speech.middleRecap', count = len(chats),
                                                   chats = chatNames, lastChat = lastChat, firstChat = firstChat)

                handler_input.response_builder.speak(speech_text).ask(speech_text)
            else:
                if len(chats) == 1:
                    del chats[0]

                sessionAttributes['state'] = States.SEND
                speech_text = handler_input.i18n.t('ReadMessageIntent.speech.middleRecap', count = 0)
                handler_input.response_builder.speak(speech_text).ask(speech_text)

        return handler_input.response_builder.response
