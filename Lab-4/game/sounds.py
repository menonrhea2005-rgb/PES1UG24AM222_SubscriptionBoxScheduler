"""Task 4: sound effects for flap, score and death.

The sounds are synthesised in code (short tones with a fade envelope), so the
game needs no extra audio files. If no audio device is available, every
play_* call silently does nothing and the game still runs.
"""
import math
import random
from array import array

import pygame


class SoundManager:
    def __init__(self, volume=0.5):
        self.enabled = False
        self.sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 2, 512)
            self.rate, fmt, self.channels = pygame.mixer.get_init()
            if fmt != -16:  # we build signed 16-bit samples
                return
            self.sounds = {
                "flap": self._sweep(450, 900, 0.09, volume * 0.6),
                "score": self._sequence([(880, 0.07), (1320, 0.12)], volume * 0.7),
                "die": self._sweep(500, 80, 0.45, volume, noise=0.25),
            }
            self.enabled = True
        except (pygame.error, TypeError):
            # No audio device (e.g. headless machine) -> run silently.
            self.enabled = False

    # ---------------------------------------------------------------- public
    def play_flap(self):
        self._play("flap")

    def play_score(self):
        self._play("score")

    def play_die(self):
        self._play("die")

    # --------------------------------------------------------------- helpers
    def _play(self, name):
        if self.enabled:
            self.sounds[name].play()

    def _to_sound(self, samples):
        """Convert floats in [-1, 1] to a pygame Sound (16-bit, N channels)."""
        buf = array("h")
        for s in samples:
            v = int(max(-1.0, min(1.0, s)) * 32767)
            buf.extend([v] * self.channels)
        return pygame.mixer.Sound(buffer=buf.tobytes())

    def _tone(self, f_start, f_end, duration, volume, noise=0.0):
        n = int(self.rate * duration)
        out, phase = [], 0.0
        for i in range(n):
            t = i / n
            freq = f_start + (f_end - f_start) * t
            phase += 2 * math.pi * freq / self.rate
            env = min(1.0, i / (0.01 * self.rate)) * (1 - t) ** 1.5  # quick attack, fade out
            s = 0.8 * math.sin(phase) + 0.2 * math.copysign(1, math.sin(phase))  # a bit "8-bit"
            if noise:
                s = (1 - noise) * s + noise * random.uniform(-1, 1)
            out.append(s * env * volume)
        return out

    def _sweep(self, f_start, f_end, duration, volume, noise=0.0):
        return self._to_sound(self._tone(f_start, f_end, duration, volume, noise))

    def _sequence(self, notes, volume):
        samples = []
        for freq, dur in notes:
            samples += self._tone(freq, freq, dur, volume)
        return self._to_sound(samples)
