from task4.audio_summary_day4 import Whisper as BaseWhisper
from task5.task5_chat_session import ChatSession



class Whisper(BaseWhisper):
    def __init__(self, chat: ChatSession) -> None:
        super().__init__(chat)
