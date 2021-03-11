import os

import pydub
from pyrogram import Client
from pyrogram.raw import functions, types

from config.aws import s3
from services.Utils import sanitizeText

pydub.AudioSegment.converter = '/opt/bin/ffmpeg'


class PyrogramService:
    """
    PyrogramService is an utility wrapper which contains methods related to Pyrogram.
    """

    def __init__(self, token = ':memory:'):
        self.client = self.createClient(token = token)

    def createClient(self, token = ':memory:'):
        """
        Creates a client and tests if it works.

        :param token: Pyrogram session token.
        :return: Pyrogram client
        """

        try:
            client = Client(
                session_name = token,
                api_id = os.getenv('TG_ID'),
                api_hash = os.getenv('TG_SECRET'),
                test_mode = False,
                app_version = os.getenv('VERSION'),
                device_model = os.getenv('DEVICE'),
                system_version = os.getenv('SYSTEM'),
                no_updates = True,
                workdir = '/tmp'
            )
            success = client.connect()

            if success:
                client.initialize()
                return client
            return False
        except ConnectionError as err:
            print(err)
            raise RuntimeError("Login error") from err

    def sendMessage(self, chatId = None, text = None, replyToMessageId = None):
        """
        Sends a text message to a chat.

        :param chatId: Chat id
        :param text: Text message
        :param replyToMessageId: Id of tagged message
        :return: True if the message is sent, otherwise false
        """

        try:
            chatId = int(chatId)
        except ValueError:
            chatId = str(chatId)

        try:
            self.client.send_message(chat_id = chatId,
                                     text = text,
                                     reply_to_message_id = replyToMessageId)
            return True
        except:
            return False

    def searchForContact(self, name = None):
        """
        Searches for a contact.

        :param name: Name of the contact to be searched
        :return: Found contact, otherwise None
        """

        try:
            request = functions.contacts.Search(q = name, limit = 1)
            response = self.client.send(request)

            if response.users:
                users = list(filter(lambda user: user.contact, response.users))
                if users:
                    return users[0]
                else:
                    users = list(filter(lambda user: False if len(self.client.send(
                        functions.messages.GetPeerDialogs(
                            peers = [types.InputDialogPeer(
                                peer = self.client.resolve_peer(user.id))])).dialogs) == 0 else True,
                                        response.users))
                    if users:
                        return users[0]
            if response.chats:
                chats = list(filter(lambda chat: not chat.left, response.chats))
                if chats:
                    return chats[0]

            return None
        except:
            return None

    def getChats(self, limit = 25):
        """
        Gets the latest chats.

        :param limit: Max chats to be retrieved
        :return: An array of chats
        """

        try:
            chats = []
            for dialog in self.client.iter_dialogs(limit = limit):
                chats.append(dialog.chat)
            return chats
        except:
            return []

    def getUnreadChats(self, limit = 20):
        """
        Gets the latest unread chats.

        :param limit: Max unread chats to be retrieved
        :return: An array of unread chats
        """

        try:
            chats = []
            unread = 0
            for dialog in self.client.iter_dialogs(limit = limit):
                if dialog.unread_messages_count > 0:
                    isMuted = self.isMuted(peerId = dialog.chat.id)
                    if not isMuted:
                        chat = {
                            'id': dialog.chat.id,
                            'username': sanitizeText(dialog.chat.username),
                            'firstname': sanitizeText(dialog.chat.first_name),
                            'lastname': sanitizeText(dialog.chat.last_name),
                            'title': sanitizeText(dialog.chat.title),
                            'type': dialog.chat.type,
                            'canReply': self.canReply(chat = dialog.chat),
                            'unreadCount': dialog.unread_messages_count
                        }
                        unread = unread + dialog.unread_messages_count
                        chats.append(chat)

            return chats, unread
        except Exception as err:
            print(err)
            return [], 0

    def getMessages(self, chatId = None, limit = 10):
        """
        Gets the latest messages from a chat. Also it sanitizes text and upload audio files to S3.

        :param chatId: Chat id
        :param limit: Max messages to be retrieved
        :return: An array of messages.
        """

        try:
            messages = []
            self.client.read_history(chat_id = chatId)
            if limit > 10:
                limit = 10
            for message in self.client.iter_history(chat_id = chatId, limit = limit):
                if not message.service:
                    text = message.text or message.caption or ''

                    if message.from_user:
                        sender = message.from_user.first_name or message.from_user.username
                    else:
                        sender = message.chat.title or message.chat.username

                    if (message.voice or message.audio) and (
                            message.voice.duration < 30 or message.voice.duration < 30):
                        fileId = message.voice.file_id or message.audio.file_id
                        isMedia = False

                        filePath = message.download(file_name = f'/tmp/{fileId}.ogg')
                        mp3 = pydub.AudioSegment.from_ogg(file = filePath)
                        mp3.export(f'/tmp/{fileId}.mp3',
                                   parameters = ['-ac', '2', '-codec:a', 'libmp3lame', '-b:a', '48k', '-ar', '24000',
                                                 '-write_xing', '0'])
                        s3.upload_file(f'/tmp/{fileId}.mp3', 'voice-gram', f'audio/{fileId}.mp3')
                    else:
                        fileId = None
                        isMedia = message.media

                    message = {'sender': sanitizeText(sender),
                               'text': sanitizeText(text),
                               'isMedia': isMedia,
                               'isService': False,
                               'fileId': fileId}
                else:
                    message = {
                        'isService': True
                    }
                messages.append(message)
            if len(messages) > 0:
                messages = list(reversed(messages))

            return messages
        except:
            return []

    def canReply(self, chat = None, chatId = None):
        """
        Checks if the user can reply to a message.

        :param chat: Chat object. Can be None, in this case chatId is set
        :param chatId: Chat id. If it's set, chat object is retrieved
        :return: True if the user can reply, otherwise False
        """

        try:
            if chat is None:
                try:
                    chatId = int(chatId)
                except ValueError:
                    chatId = str(chatId)

                chat = self.client.get_chat(chatId)
            if chat.type == 'group' or chat.type == 'supergroup':
                return chat.permissions.can_send_messages
            elif chat.type == 'channel':
                chatMember = self.client.get_chat_member(chat_id = chat.id, user_id = 'self')
                return chatMember.status != 'member'

            return True
        except:
            return False

    def logout(self):
        """
        Logs the user out.

        :return: True if the user logs out successfully, otherwise False
        """

        try:
            self.client.log_out()
            return True
        except:
            return False

    def isMuted(self, peerId = None):
        """
        Checks if the chat is muted.

        :param peerId: Similar to chat id
        :return: True if the chat is muted, otherwise False
        """

        try:
            request = functions.account.GetNotifySettings(
                peer = types.InputNotifyPeer(peer = self.client.resolve_peer(peer_id = peerId)))
            response = self.client.send(request)

            if response.mute_until is None or response.mute_until == 0:
                return False
            else:
                return True
        except:
            return None

    def getFirstName(self):
        """
        Gets the firstname of the logged in user.

        :return: Sanitized firstname
        """

        try:
            return sanitizeText(text = self.client.get_me().first_name)
        except:
            return ''
