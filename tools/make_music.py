"""Pre-render 5 seamlessly-looping soft-synthwave tracks to music/track_N.wav.
Pure stdlib (original algorithmic synthesis). Run from repo root: python tools/make_music.py"""
import array
import math
import os
import wave

SR = 44100
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "music")


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12.0)


# (bpm, root_midi, [4 triads as semitone offsets]) — five gentle minor-ish moods
TRACKS = [
    (92,  57, [[0, 3, 7], [-2, 3, 7], [-4, 0, 3], [-5, 2, 7]]),
    (100, 60, [[0, 3, 7], [5, 8, 12], [3, 7, 10], [-2, 2, 5]]),
    (88,  53, [[0, 4, 7], [-3, 0, 4], [2, 5, 9], [-5, -1, 2]]),
    (104, 55, [[0, 3, 7], [-5, -2, 2], [-4, 0, 3], [-2, 1, 5]]),
    (96,  58, [[0, 3, 8], [-1, 4, 7], [-4, 0, 5], [-6, -2, 1]]),
]


def render(bpm, root, chords):
    beat = 60.0 / bpm
    bar = beat * 4
    total = bar * len(chords)              # loop = 4 bars
    n = int(total * SR)
    buf = [0.0] * n
    for i in range(n):
        t = i / SR
        chord = chords[int(t / bar) % len(chords)]
        s = 0.0
        for off in chord:                  # warm pad triad
            s += 0.16 * math.sin(2 * math.pi * midi(root + off) * t)
        s += 0.22 * math.sin(2 * math.pi * midi(root + chord[0] - 12) * t)   # bass
        an = chord[int(t / (beat / 2)) % len(chord)]                          # 8th-note arp
        ph = (t % (beat / 2)) / (beat / 2)
        s += 0.15 * max(0.0, 1.0 - ph) ** 2 * math.sin(2 * math.pi * midi(root + an + 12) * t)
        kph = (t % beat) / beat                                               # soft kick
        kenv = max(0.0, 1.0 - kph * 6)
        if kenv > 0:
            s += 0.5 * kenv * math.sin(2 * math.pi * (90 - 45 * min(1.0, kph * 6)) * t)
        buf[i] = s
    # seamless wrap: crossfade tail into head (~15ms)
    fade = min(660, n // 8)
    for k in range(fade):
        a = k / fade
        buf[n - fade + k] = buf[n - fade + k] * (1 - a) + buf[k] * a
    peak = max(1e-6, max(abs(x) for x in buf))
    g = 0.82 / peak
    return array.array("h", (int(max(-1.0, min(1.0, x * g)) * 32767) for x in buf))


def main():
    os.makedirs(OUT, exist_ok=True)
    for i, (bpm, root, chords) in enumerate(TRACKS, 1):
        samples = render(bpm, root, chords)
        with wave.open(os.path.join(OUT, f"track_{i}.wav"), "w") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(samples.tobytes())
        print(f"track_{i}.wav  {len(samples)} samples")


if __name__ == "__main__":
    main()
