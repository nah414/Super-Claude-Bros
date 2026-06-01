"""Synthesized sound effects (pure stdlib, no numpy).

Builds short int16 PCM tones with `array`/`math` and feeds the raw buffer to
pygame.mixer.Sound. Degrades to silent no-ops if there's no audio device.
"""
import array
import math
import pygame
from game import settings as S


class SoundFX:
    def __init__(self):
        self.enabled = False
        self.sounds = {}
        try:
            pygame.mixer.pre_init(S.SAMPLE_RATE, -16, 1)
            pygame.mixer.init()
            self._build()
            self.enabled = True
        except Exception:
            self.enabled = False

    def _tone(self, freqs, dur=0.12, vol=0.35):
        n = int(S.SAMPLE_RATE * dur)
        amp = vol * 32767
        k = len(freqs)
        buf = array.array("h", bytes(2 * n))     # n signed-16 samples, zeroed
        for i in range(n):
            t = i / S.SAMPLE_RATE
            s = 0.0
            for f in freqs:
                s += math.sin(2 * math.pi * f * t)
            s /= k
            v = int(s * amp * (1.0 - i / n) ** 1.5)   # decay envelope
            buf[i] = 32767 if v > 32767 else (-32768 if v < -32768 else v)
        return pygame.mixer.Sound(buffer=buf.tobytes())

    def _build(self):
        self.sounds = {
            "jump":   self._tone([440, 660], 0.12),
            "double": self._tone([660, 990], 0.12),
            "token":  self._tone([880, 1320], 0.09),
            "stomp":  self._tone([320, 180], 0.12),
            "power":  self._tone([523, 659, 784], 0.22),
            "hurt":   self._tone([392, 233], 0.22),
            "win":    self._tone([523, 659, 784, 1047], 0.40),
        }

    def play(self, name):
        if not self.enabled:
            return
        s = self.sounds.get(name)
        if s:
            s.play()
