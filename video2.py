from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService
# from manim_voiceover.services.recorder import RecorderService


class Video2(VoiceoverScene):
    def construct(self):
        self.set_speech_service(GTTSService(transcription_model="base"))
        # self.set_speech_service(RecorderService())

        with self.voiceover("") as tracker:
            pass
