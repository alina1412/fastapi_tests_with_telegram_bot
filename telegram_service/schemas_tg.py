from dataclasses import dataclass


@dataclass
class MessageInCallbackDto:
    chat_id: int
    callback_data: dict


@dataclass
class MessageInTextDto:
    chat_id: int
    text_input: str
