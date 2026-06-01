"""Synthesized sound effects. Degrades to silent no-ops if audio/numpy is unavailable."""
import pygame
from game import settings as S

try:
    import numpy as np
except Exception:
    np = None


class SoundFX:
    def __init__(self):
        self.enabled = False
        self.sounds = {}
        if np is None:
            return
        try:
            pygame.mixer.pre_init(S.SAMPLE_RATE, -16, 1)
            pygame.mixer.init()
            self._build()
            self.enabled = True
        except Exception:
            self.enabled = False

    def _tone(self, freqs, dur=0.12, vol=0.35):
        n = int(S.SAMPLE_RATE * dur)
        t = np.linspace(0, dur, n, False)
        wave = sum(np.sin(2 * np.pi * f * t) for f in freqs) / len(freqs)
        wave *= np.linspace(1, 0, n) ** 1.5             # decay envelope
        return pygame.sndarray.make_sound((wave * vol * 32767).astype(np.int16))

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
