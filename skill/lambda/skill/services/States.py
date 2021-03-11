from enum import Enum


class States(Enum):
    """
    Enumeration of skill states.
    """

    SEND = 'SEND'
    SEND_AGAIN = 'SEND_AGAIN'
    READ = 'READ'
    REPLY = 'REPLY'
