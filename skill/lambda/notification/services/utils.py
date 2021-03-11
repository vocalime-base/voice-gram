import logging
import os
import uuid
from datetime import timedelta, datetime

from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_core.serialize import DefaultSerializer
from ask_sdk_model.services.api_configuration import ApiConfiguration
from ask_sdk_model.services.authentication_configuration import AuthenticationConfiguration
from ask_sdk_model.services.proactive_events import Event, CreateProactiveEventRequest, RelevantAudience, \
    RelevantAudienceType, SkillStage
from ask_sdk_model.services.proactive_events.proactive_events_service_client import ProactiveEventsServiceClient

from resources.locales import locales

logger = logging.getLogger()


def sanitizeText(text = ''):
    """
    Removes special characters from the input text.

    :param text: String
    :return: Sanitized text
    """

    try:
        text = text.encode('ascii', 'ignore').decode('ascii').strip()
        text = text.replace('&', ' ')
        return text
    except ValueError as err:
        logger.error(str(err))
        return ''


def createClient(endpoint = ''):
    """
    Creates Service Client used to make API requests.

    :param endpoint: Alexa region endpoint.
    :return: ServiceClient
    """

    client = ProactiveEventsServiceClient(
        api_configuration = ApiConfiguration(
            serializer = DefaultSerializer(),
            api_client = DefaultApiClient(),
            api_endpoint = endpoint),
        authentication_configuration = AuthenticationConfiguration(
            client_id = os.getenv('ALEXA_ID'),
            client_secret = os.getenv('ALEXA_SECRET')))

    return client


def sendEvent(endpoint = '', userId = '', names = '', unreadCount = 0, locale = 'en-US', username = ''):
    """
    Send the notification to Alexa.

    :param endpoint: Alexa region endpoint
    :param userId: Alexa user id
    :param names: Sender names
    :param unreadCount: Count of unread messages
    :param locale: User locale
    :param username: Username
    :return: None
    """
    event = Event(
        name = "AMAZON.MessageAlert.Activated",
        payload = {
            "state": {
                "status": "UNREAD",
                "freshness": "NEW"
            },
            "messageGroup": {
                "creator": {
                    "name": locales.get(locale).replace('%{names}', ', '.join(names)).replace('%{username}', username)
                },
                "count": unreadCount
            }
        }
    )

    create_event = CreateProactiveEventRequest(
        timestamp = datetime.utcnow(),
        reference_id = str(uuid.uuid4()),
        expiry_time = datetime.utcnow() + timedelta(hours = 1),
        event = event,
        relevant_audience = RelevantAudience(
            object_type = RelevantAudienceType.Unicast,
            payload = {
                'user': userId
            }
        )
    )

    createClient(endpoint = endpoint).create_proactive_event(
        create_proactive_event_request = create_event,
        stage = SkillStage.DEVELOPMENT)
