from enum import Enum, auto


class Sender(Enum):
    USER = auto()
    ASSISTANT = auto()


class Role(Enum):
    USER = auto()
    ASSISTANT = auto()
    SYSTEM = auto()
