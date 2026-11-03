from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService
# from manim_voiceover.services.recorder import RecorderService


class Video1(VoiceoverScene):
    def construct(self):
        self.set_speech_service(GTTSService(transcription_model="base"))
        # self.set_speech_service(RecorderService())

        title = Title(r"Proof: if n is an odd integer, then $n^2$ is odd")
        another = MarkupText(
            f'<span fgcolor="{BLUE}">Proof</span>: if <span fgcolor="{RED}">n</span> is an odd integer, then <span fgcolor="{RED}">n²</span> is odd',
            color=WHITE,
            font_size=40,
        )
        with self.voiceover(
            "Today we are going to prove that if n is an odd integer, then n squared is odd"
        ) as tracker:
            self.play(Write(another), run_time=tracker.duration)
            self.play(Transform(another, title))

        text = MathTex("n", "=", "2k + 1").next_to(title, DOWN)
        with self.voiceover(
            "An odd integer can be written as n is equal to 2k plus 1, where k is an integer."
        ) as tracker:
            self.play(Create(text), run_time=tracker.duration)

        text2 = MathTex("n^2", "=", "(2k + 1)^2").next_to(text, DOWN)
        text3 = MathTex("4k^2 + 4k", " + 1").next_to(text2[1], RIGHT)
        with self.voiceover("Square both sides") as tracker:
            self.play(TransformFromCopy(text, text2), run_time=tracker.duration / 2)
            self.play(
                ReplacementTransform(text2[2], text3), run_time=tracker.duration / 2
            )

        text4 = MathTex("2(2k^2 + 2k)", " + 1").next_to(text2[1], RIGHT)
        with self.voiceover("Factor out a 2 from the first two terms") as tracker:
            self.play(ReplacementTransform(text3, text4), run_time=tracker.duration)

        text5 = MathTex("m = 2k^2 + 2k").next_to(text2, DOWN, aligned_edge=LEFT)
        with self.voiceover(
            "Let m is equal to 2 k squared plus 2 k. Since k is an integer, m is also an integer"
        ) as tracker:
            self.play(Write(text5), run_time=tracker.duration)

        text6 = MathTex("n^2", "=", "2m + 1").next_to(text2, DOWN)
        with self.voiceover(
            "Thus, <bookmark mark='insc_csc'/> n squared is equal to 2 em plus 1, which matches the definition of an odd number."
        ) as tracker:
            self.play(text5.animate.shift(RIGHT * 5))
            rect = SurroundingRectangle(text5, buff=0.1)
            self.play(Create(rect))
            self.wait_until_bookmark("insc_csc")
            self.play(TransformFromCopy(text2, text6))
