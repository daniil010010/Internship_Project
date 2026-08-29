import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / "Task 4")
)

from audio_summary_day4 import Whisper as BaseWhisper



class Whisper(BaseWhisper):
    def __init__(self) -> None:
        super().__init__()
