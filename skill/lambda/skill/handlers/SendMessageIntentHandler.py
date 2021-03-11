from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name, get_slot
from ask_sdk_model.dialog.elicit_slot_directive import ElicitSlotDirective
from ask_sdk_model.slot import Slot
from ask_sdk_model.slu.entityresolution.status_code import StatusCode

from services.States import States
from services.Utils import createFilledElicitSlotDirective, createEmptyElicitSlotDirective


def checkReceiver(chatNameSlot, client):
    if len(chatNameSlot.resolutions.resolutions_per_authority) > 1 and \
            chatNameSlot.resolutions.resolutions_per_authority[
                1].status.code == StatusCode.ER_SUCCESS_MATCH:
        chatId = chatNameSlot.resolutions.resolutions_per_authority[
            1].values[0].value.id
        chatNameValue = chatNameSlot.resolutions.resolutions_per_authority[
            1].values[0].value.name
    else:
        if chatNameSlot.resolutions.resolutions_per_authority[0].status.code == StatusCode.ER_SUCCESS_MATCH:
            chatNameValue = chatNameSlot.resolutions.resolutions_per_authority[
                0].values[0].value.name
            chatId = chatNameSlot.resolutions.resolutions_per_authority[
                0].values[0].value.id
        else:
            chatNameValue = chatNameSlot.value
            chat = client.searchForContact(name = chatNameValue)
            if chat:
                chatId = chat.id
            else:
                chatId = None

    return chatId, chatNameValue


class SendMessageIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type('IntentRequest')(handler_input) and is_intent_name('SendMessageIntent')(handler_input)

    def handle(self, handler_input):
        """
        Una volta che sono in questo intent ho 4 possibilità:
        1- Nessuno degli slot è completato quindi parto a chiedere il destinatario
        2- Il destinatario è completo allora chiedo il testo
        3- Il testo è completo quindi chiedo il destinatario
        4- Ho entrambi i campi, quindi chiedo se vuole aggiungere altro o inviare
        :param handler_input:
        :return:
        """
        sessionAttributes = handler_input.attributes_manager.session_attributes
        requestAttributes = handler_input.attributes_manager.request_attributes

        if not sessionAttributes['isAuthorized']:
            speech_text = handler_input.i18n.t('Errors.noAccountLinked')
            handler_input.response_builder.speak(speech_text).set_should_end_session(True)

            return handler_input.response_builder.response

        sessionAttributes['state'] = States.SEND

        chatNameSlot = get_slot(handler_input, 'chatName')
        textSlotValue = get_slot(handler_input, 'text').value
        actionSlot = get_slot(handler_input, 'action')

        client = requestAttributes['tg']
        if not chatNameSlot.value and not actionSlot.value:
            sessionAttributes['write'] = {'text': []}
            speech_text = handler_input.i18n.t('SendMessageIntent.elicit.chatName')
            return handler_input.response_builder.speak(speech_text).add_directive(
                ElicitSlotDirective(slot_to_elicit = 'chatName')).response
        elif not textSlotValue and not actionSlot.value:
            chatId, chatNameValue = checkReceiver(chatNameSlot, client)
            canReply = client.canReply(chatId = chatId)
            if not chatId or not canReply:
                if not canReply:
                    speech_text = handler_input.i18n.t('SendMessageIntent.speech.cantReply', chatName = chatNameValue)
                else:
                    speech_text = handler_input.i18n.t('SendMessageIntent.speech.chatNotFound',
                                                       chatName = chatNameValue)
                intent = handler_input.request_envelope.request.intent
                intent.slots['chatName'] = Slot(name = 'chatName')
                repeatChatName = handler_input.i18n.t('SendMessageIntent.elicit.repeatChatName')
                return handler_input.response_builder.speak(speech_text + repeatChatName).add_directive(
                    createEmptyElicitSlotDirective(slotName = 'chatName', updatedIntent = intent)).response

            sessionAttributes['write']['chat'] = {'id': chatId, 'name': chatNameValue}
            speech_text = handler_input.i18n.t(
                'SendMessageIntent.speech.chatFound', chatName = chatNameValue) + handler_input.i18n.t(
                'SendMessageIntent.elicit.text')
            return handler_input.response_builder.speak(speech_text).add_directive(
                ElicitSlotDirective(slot_to_elicit = 'text')).response
        elif not actionSlot.value:
            sessionAttributes['write']['temp'] = textSlotValue
            speech_text = handler_input.i18n.t(
                'SendMessageIntent.speech.textCheck', text = textSlotValue) + handler_input.i18n.t(
                'SendMessageIntent.elicit.action')
            return handler_input.response_builder.speak(speech_text).add_directive(
                ElicitSlotDirective(slot_to_elicit = 'action')).response
        else:
            if actionSlot.resolutions.resolutions_per_authority[0].status.code == StatusCode.ER_SUCCESS_MATCH:
                action = actionSlot.resolutions.resolutions_per_authority[0].values[0].value.id
                sessionAttributes['write']['text'].append(textSlotValue or sessionAttributes['write']['temp'])
                if action == 'sendMessage':
                    chatId = sessionAttributes['write']['chat']['id']
                    chatNameValue = sessionAttributes['write']['chat']['name']
                    if chatId:
                        sessionAttributes['write']['text'] = list(
                            (msg.capitalize() for msg in sessionAttributes['write']['text']))
                        separator = '. '
                        text = separator.join(
                            sessionAttributes['write']['text'])
                        sent = client.sendMessage(chatId = chatId, text = text)
                        if sent:
                            sessionAttributes['state'] = States.SEND_AGAIN
                            speech_text = handler_input.i18n.t('SendMessageIntent.speech.messageSent',
                                                               chatName = chatNameValue)
                        else:
                            speech_text = handler_input.i18n.t('SendMessageIntent.speech.messageNotSent')

                        handler_input.response_builder.speak(speech_text).ask(speech_text)
                elif action == 'edit':
                    sessionAttributes['write']['text'] = sessionAttributes['write']['text'][:-1]
                    speech_text = handler_input.i18n.t('SendMessageIntent.elicit.text')
                    chatId = sessionAttributes['write']['chat']['id']
                    chatName = sessionAttributes['write']['chat']['name']
                    handler_input.response_builder.speak(speech_text).add_directive(
                        createFilledElicitSlotDirective(slotName = 'text', chatName = chatName, chatId = chatId))
                else:
                    intent = handler_input.request_envelope.request.intent
                    intent.slots['action'] = Slot(name = 'action')
                    intent.slots['text'] = Slot(name = 'text')
                    speech_text = handler_input.i18n.t('SendMessageIntent.elicit.appendText')

                    handler_input.response_builder.speak(speech_text).add_directive(
                        createEmptyElicitSlotDirective(slotName = 'text', updatedIntent = intent))
            else:
                speech_text = handler_input.i18n.t('SendMessageIntent.elicit.action')
                intent = handler_input.request_envelope.request.intent
                intent.slots['action'] = Slot(name = 'action')

                handler_input.response_builder.speak(speech_text).add_directive(
                    createEmptyElicitSlotDirective(slotName = 'action', updatedIntent = intent))

        return handler_input.response_builder.response
