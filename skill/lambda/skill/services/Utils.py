import os
import re

from ask_sdk_model import Intent, Slot
from ask_sdk_model.dialog import ElicitSlotDirective
from ask_sdk_model.er.dynamic.entity import Entity
from ask_sdk_model.er.dynamic.entity_list_item import EntityListItem
from ask_sdk_model.er.dynamic.entity_value_and_synonyms import EntityValueAndSynonyms
from ask_sdk_model.slu.entityresolution.resolution import Resolution
from ask_sdk_model.slu.entityresolution.resolutions import Resolutions
from ask_sdk_model.slu.entityresolution.status import Status
from ask_sdk_model.slu.entityresolution.status_code import StatusCode
from ask_sdk_model.slu.entityresolution.value import Value
from ask_sdk_model.slu.entityresolution.value_wrapper import ValueWrapper

from config.aws import s3

specialXMLCharsMap = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&apos;'
}


def getChatListElements(chats = None):
    """
    Gets a list of chat objects and returns a list of names.

    :param chats: List of chats
    :return: asdads
    """

    if chats is None:
        chats = []

    names = list(map(lambda chat: getChatName(chat), chats))
    comma = ', '
    chatNames = comma.join(names[:-1])
    firstChat = names[0]
    lastChat = names[-1]

    return chatNames, firstChat, lastChat


def sanitizeText(text):
    """
    Removes special characters, urls and emotes from text message.

    :param text: String of text
    :return: Sanitized text
    """

    try:
        text = text.encode('ascii', 'ignore').decode('ascii').strip()
        text = re.sub(r'[&\'"><]', lambda match: specialXMLCharsMap.get(match.group(0), ''), text)
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        return text
    except:
        return ''


def getChatName(chat):
    """
    Gets chat name/username/title of the chat.

    :param chat: Chat object
    :return: Chat name
    """

    text = chat.get('firstname') or chat.get('title') or chat.get('username')
    return text


def formatMessages(chat, i18n):
    """
    Compose messages adding audio files, chat name, etc.

    :param chat: Chat object
    :param i18n: i18n object
    :return: Formatted text
    """

    prec = None
    messageTexts = []
    isGroup = chat.get('type') == 'group' or chat.get('type') == 'supergroup'

    for message in chat.get('messages'):
        if message.get('isService'):
            messageTexts.append(i18n.t('ReadMessageIntent.speech.service'))
            continue
        if message.get('fileId'):
            url = s3.generate_presigned_url('get_object',
                                            Params = {'Bucket': os.getenv("PROJECT_NAME"),
                                                      'Key': f'audio/{message.get("fileId")}.mp3'},
                                            ExpiresIn = 60)
            url = re.sub(r'[&\'"><]', lambda match: specialXMLCharsMap.get(match.group(0), ''), url)
            message['text'] = f'<audio src="{url}" />'
        if isGroup:
            if message.get('sender') == prec:
                messageTexts.append(message.get('text'))
            else:
                prec = message.get('sender')
                messageTexts.append(i18n.t('ReadMessageIntent.speech.groupMessage',
                                           sender = prec,
                                           text = message.get('text')))

        else:
            messageTexts.append(message.get('text'))

        if message.get('isMedia'):
            messageTexts.append(i18n.t('ReadMessageIntent.speech.media'))

    separator = ' <break strength="strong"/> '
    return separator.join(messageTexts)


def createEmptyElicitSlotDirective(slotName = '', updatedIntent = None):
    """
    Builds slot directive.

    :param slotName: Alexa dialog slot name
    :param updatedIntent: Alexa dialog intent
    :return: SlotDirective
    """

    return ElicitSlotDirective(slot_to_elicit = slotName,
                               updated_intent = updatedIntent if updatedIntent else Intent(name = 'SendMessageIntent',
                                                                                           slots = {
                                                                                               'chatName': Slot(
                                                                                                   name = 'chatName'),
                                                                                               'text': Slot(
                                                                                                   name = 'text'),
                                                                                               'action': Slot(
                                                                                                   name = 'action')}))


def createFilledElicitSlotDirective(slotName = '', chatName = '', chatId = ''):
    """
    Fills slot directive.

    :param slotName: Alexa slot name
    :param chatName: Chat name
    :param chatId: Chat id
    :return: SlotDirective
    """

    return ElicitSlotDirective(slot_to_elicit = slotName,
                               updated_intent = Intent(name = 'SendMessageIntent', slots = {
                                   'chatName': Slot(name = 'chatName',
                                                    value = chatName,
                                                    resolutions = Resolutions(resolutions_per_authority = [
                                                        Resolution(
                                                            authority = f'amzn1.er-authority.echo-sdk.{os.getenv("SKILL_ID")}.chatNameSlot',
                                                            status = Status(
                                                                code = StatusCode.ER_SUCCESS_MATCH),
                                                            values = [ValueWrapper(
                                                                value = Value(name =
                                                                              chatName,
                                                                              id =
                                                                              chatId))])])),
                                   'text': Slot(name = 'text'), 'action': Slot(name = 'action')}))


def createChatNameDynamicEntities(client):
    """
    Generates dynamic entities from the latest 25 chats.

    :param client: Pyrogram client
    :return: Dynamic entities
    """

    chats = client.getChats()

    def createValue(chat):
        synonyms = []

        if chat.type == 'private' or chat.type == 'bot':
            value = sanitizeText(chat.first_name)
            if chat.last_name:
                lastName = sanitizeText(chat.last_name)
                synonyms.append(f'{value} {lastName}')
                synonyms.append(lastName)
        else:
            value = sanitizeText(chat.title)
        if chat.username:
            synonyms.append(sanitizeText(chat.username.replace('_', ' ')))

        return Entity(id = chat.id, name = EntityValueAndSynonyms(value = value, synonyms = synonyms))

    values = list(map(createValue, chats))
    values = list(filter(lambda el: el.name.value != '', values))

    return [EntityListItem(name = 'chatNameSlot', values = values)]
