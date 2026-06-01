"""Loops one pre-rendered track per level. Silent no-op if no audio device."""
import pygame
from game import settings as S
from game import levelset


class MusicManager:
    def __init__(self):
        self.enabled = pygame.mixer.get_init() is not None
        self.current = None
        if self.enabled:
            try:
                pygame.mixer.music.set_volume(S.MUSIC_VOLUME)
            except Exception:
                self.enabled = False

    def play_for_level(self, index):
        if not self.enabled:
            return
        track = levelset.track_number(index)
        if track == self.current:
            return
        self.current = track
        try:
            pygame.mixer.music.load(S.resource_path(f"music/track_{track}.wav"))
            pygame.mixer.music.play(loops=-1)
        except Exception:
            self.enabled = False

    def stop(self):
        if self.enabled:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
        self.current = None
