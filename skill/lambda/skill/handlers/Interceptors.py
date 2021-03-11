import os

from ask_sdk_core.dispatch_components import AbstractRequestInterceptor, AbstractResponseInterceptor
from ask_sdk_core.exceptions import AttributesManagerException
from ask_sdk_core.utils import get_locale

from config.i18n import i18n
from services.PyrogramService import PyrogramService


class RequestInterceptor(AbstractRequestInterceptor):
    def process(self, handler_input):
        try:
            sessionAttributes = handler_input.attributes_manager.session_attributes
            requestAttributes = handler_input.attributes_manager.request_attributes
        except AttributesManagerException:
            return

        # Set locale
        locale = get_locale(handler_input)
        if locale is not None:
            i18n.set('locale', locale)
            handler_input.i18n = i18n

        requestAttributes['tg'] = PyrogramService(os.getenv("TG_TOKEN"))
        if requestAttributes['tg'].client:
            sessionAttributes['isAuthorized'] = True
        else:
            sessionAttributes['isAuthorized'] = False


class ResponseInterceptor(AbstractResponseInterceptor):
    def process(self, handler_input, response):
        requestAttributes = handler_input.attributes_manager.request_attributes

        if 'tg' in requestAttributes and requestAttributes['tg'].client:
            requestAttributes['tg'].client.terminate()
            requestAttributes['tg'].client.disconnect()
