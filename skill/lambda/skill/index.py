"""
Import handlers
"""

from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_core.skill_builder import CustomSkillBuilder

from handlers.CancelIntentHandler import CancelIntentHandler
from handlers.FallbackIntentHandler import FallbackIntentHandler
from handlers.HelpIntentHandler import HelpIntentHandler
from handlers.Interceptors import RequestInterceptor, ResponseInterceptor
from handlers.LaunchRequestHandler import LaunchRequestHandler
from handlers.ReadMessageIntentHandler import ReadMessageIntentHandler
from handlers.RepeatIntentHandler import RepeatIntentHandler
from handlers.SendMessageIntentHandler import SendMessageIntentHandler
from handlers.SessionEndedRequestHandler import SessionEndedRequestHandler, ErrorHandler
from handlers.StopIntentHandler import StopIntentHandler
from handlers.YesNoIntentHandlers import YesIntentHandler, NoIntentHandler

"""
Create CustomSkillBuilder and add request/exception handlers
"""

sb = CustomSkillBuilder(api_client = DefaultApiClient())

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(SendMessageIntentHandler())
sb.add_request_handler(ReadMessageIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(YesIntentHandler())
sb.add_request_handler(NoIntentHandler())
sb.add_request_handler(RepeatIntentHandler())
sb.add_request_handler(CancelIntentHandler())
sb.add_request_handler(StopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(ErrorHandler())

sb.add_global_request_interceptor(RequestInterceptor())
sb.add_global_response_interceptor(ResponseInterceptor())

"""
Lambda handler
"""

handler = sb.lambda_handler()
