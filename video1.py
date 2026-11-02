from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService
# from manim_voiceover.services.recorder import RecorderService

class Video1(VoiceoverScene):
    def construct(self):
        self.set_speech_service(GTTSService())
        # self.set_speech_service(RecorderService())

        with self.voiceover("Hello, World") as tracker:
            self.play(Write(Text("Hello, World!")))
