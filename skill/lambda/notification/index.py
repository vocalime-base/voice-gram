import logging
import os

from services.PyrogramService import PyrogramService
from services.utils import sendEvent

logger = logging.getLogger()

# Used to cache Telegram client instead of reconnect them on every call
cache = {}


def handler(event, context):
    global cache

    try:
        userId = os.getenv('ALEXA_USER_ID')
        if 'client' not in cache:
            client = PyrogramService(token = os.getenv('TG_TOKEN'))
            cache['client'] = client
        else:
            client = cache['client']

        logger.info(f"Checking unread chats for user {userId}")
        names, unreadCount = client.getUnreadChats(limit = 10)
        username = client.getFirstname()

        namesHash = hash(frozenset(names))

        if unreadCount != 0 and (namesHash != cache.get('namesHash') or
                                 unreadCount != cache.get(userId).get('unreadCount')):
            logger.info(f'User {userId} has {unreadCount} new unread messages')

            cache['namesHash'] = namesHash
            cache['unreadCount'] = unreadCount

            sendEvent(endpoint = os.getenv('ENDPOINT'), userId = userId, username = username,
                      locale = os.getenv('LOCALE', 'en-US'), names = names, unreadCount = unreadCount)
        else:
            logger.info(f'User {userId} has {unreadCount} old unread messages')
    except RuntimeError as err:
        logger.error(f'Error: {str(err)}')
