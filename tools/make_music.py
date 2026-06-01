"""Pre-render 5 *distinct* seamlessly-looping tracks to music/track_N.wav.
Pure stdlib, original algorithmic synthesis. Each track has its own waveforms,
tempo, rhythm and instrumentation so they sound clearly different from one another.
Run from repo root: python tools/make_music.py"""
import array
import math
import os
import wave

SR = 44100
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "music")


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12.0)


def osc(wave_, f, t):
    ph = (f * t) % 1.0
    if wave_ == "sine":
        return math.sin(2 * math.pi * f * t)
    if wave_ == "saw":
        return 2.0 * ph - 1.0
    if wave_ == "square":
        return 1.0 if ph < 0.5 else -1.0
    if wave_ == "tri":
        return 4.0 * abs(ph - 0.5) - 1.0
    return 0.0


# Five distinct moods. Each: tempo, key, chord loop, and which voices play (with waveforms).
#   pad/bass = (waveform, level) or None ; arp = (waveform, level, notes_per_beat) or None
#   kick = (pattern, level) or None  (pattern: "four"=every beat, "two"=beats 1&3)
#   hat  = level or None  (offbeat hi-hat tick)
TRACKS = [
    dict(name="dawn",   bpm=76,  root=57, chords=[[0, 3, 7], [-4, 0, 3], [2, 5, 9], [-2, 2, 5]],
         pad=("sine", 0.24), bass=("sine", 0.18), arp=None,                kick=None,          hat=None),
    dict(name="pulse",  bpm=100, root=60, chords=[[0, 3, 7], [5, 8, 12], [-2, 3, 7], [-4, 0, 3]],
         pad=("sine", 0.16), bass=("saw", 0.20),  arp=None,                kick=("four", 0.5), hat=None),
    dict(name="arcade", bpm=112, root=55, chords=[[0, 4, 7], [2, 5, 9], [-3, 0, 4], [-1, 2, 7]],
         pad=("tri", 0.09),  bass=("sine", 0.18), arp=("square", 0.17, 4), kick=("two", 0.46), hat=0.10),
    dict(name="neon",   bpm=124, root=53, chords=[[0, 3, 7], [-2, 3, 7], [-4, 0, 5], [-5, -1, 2]],
         pad=("saw", 0.11),  bass=("saw", 0.20),  arp=("saw", 0.12, 2),    kick=("four", 0.5), hat=0.12),
    dict(name="voyage", bpm=90,  root=58, chords=[[0, 3, 8], [-1, 4, 7], [-4, 0, 5], [2, 5, 9]],
         pad=("tri", 0.18),  bass=("sine", 0.22), arp=("tri", 0.10, 2),    kick=("two", 0.4),  hat=None),
]


def render(cfg):
    beat = 60.0 / cfg["bpm"]
    bar = beat * 4
    chords = cfg["chords"]
    total = bar * len(chords)
    n = int(total * SR)
    root = cfg["root"]
    buf = [0.0] * n
    for i in range(n):
        t = i / SR
        chord = chords[int(t / bar) % len(chords)]
        s = 0.0
        if cfg["pad"]:
            w, lv = cfg["pad"]
            for off in chord:
                s += lv * osc(w, midi(root + off), t)
        if cfg["bass"]:
            w, lv = cfg["bass"]
            s += lv * osc(w, midi(root + chord[0] - 12), t)
        if cfg["arp"]:
            w, lv, rate = cfg["arp"]
            step = beat / rate
            an = chord[int(t / step) % len(chord)]
            ph = (t % step) / step
            s += lv * max(0.0, 1.0 - ph) ** 2 * osc(w, midi(root + an + 12), t)
        if cfg["kick"]:
            pat, lv = cfg["kick"]
            bpos = (t % beat) / beat
            beatidx = int(t / beat) % 4
            if pat == "four" or (pat == "two" and beatidx in (0, 2)):
                env = max(0.0, 1.0 - bpos * 6)
                if env > 0:
                    s += lv * env * math.sin(2 * math.pi * (95 - 50 * min(1.0, bpos * 6)) * t)
        if cfg["hat"]:
            half = beat / 2
            if int(t / half) % 2 == 1:                      # the "&" offbeats
                hpos = (t % half) / half
                env = max(0.0, 1.0 - hpos * 22)
                if env > 0:
                    s += cfg["hat"] * env * osc("square", 9000, t)
        buf[i] = s
    fade = min(660, n // 8)                                  # seamless loop wrap
    for k in range(fade):
        a = k / fade
        buf[n - fade + k] = buf[n - fade + k] * (1 - a) + buf[k] * a
    peak = max(1e-6, max(abs(x) for x in buf))
    g = 0.8 / peak
    return array.array("h", (int(max(-1.0, min(1.0, x * g)) * 32767) for x in buf))


def main():
    os.makedirs(OUT, exist_ok=True)
    for i, cfg in enumerate(TRACKS, 1):
        samples = render(cfg)
        with wave.open(os.path.join(OUT, f"track_{i}.wav"), "w") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(samples.tobytes())
        print(f"track_{i}.wav ({cfg['name']}) {len(samples)} samples")


if __name__ == "__main__":
    main()
