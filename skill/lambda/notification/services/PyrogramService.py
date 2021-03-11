import os

from pyrogram import Client
from pyrogram.raw import functions, types

from services.utils import sanitizeText


class PyrogramService:

    def __init__(self, token = ':memory:'):
        self.client = self.createClient(token)

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
                return client
            return False
        except ConnectionError as err:
            print(err)
            raise RuntimeError("Login error") from err

    def getUnreadChats(self, limit = 20):
        """
        Gets the latest unread chats.

        :param limit: Max unread chats to be retrieved
        :return: An array of unread chats
        """

        try:
            names = []
            unreadCount = 0
            for dialog in self.client.iter_dialogs(limit = limit):
                if dialog.unread_messages_count > 0:
                    isMuted = self.isMuted(peerId = dialog.chat.id)
                    if not isMuted or dialog.unread_mentions_count > 0:
                        name = dialog.chat.first_name or dialog.chat.title or dialog.chat.username
                        names.append(sanitizeText(name))
                        unreadCount = unreadCount + dialog.unread_messages_count

            return names, unreadCount
        except:
            return [], 0

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

    def getFirstname(self):
        """
        Gets the firstname of the logged in user.

        :return: Firstname
        """

        try:
            return self.client.get_me().first_name
        except:
            return ''
