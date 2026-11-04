"""Synthesised sounds for the pack: mob voices (goblins, trolls, wolves, undead, wraiths, demons, dragons, frost and
void creatures), and an epic theme for entering the guild city. Everything is generated with numpy (no samples),
deterministic (fixed seeds) and encoded to Ogg Vorbis with ffmpeg in bit-exact mode, so the pack hash stays stable.
"""
import math
import os
import subprocess
import tempfile
import wave
import zlib

import numpy as np

SR = 44100


# ====================================================================== basics

def t_axis(seconds):
    return np.arange(int(seconds * SR)) / SR


def env(n, attack=0.01, release=0.2, curve=2.0):
    """Attack/decay envelope over n samples (seconds for attack/release)."""
    e = np.ones(n)
    a = max(1, int(attack * SR))
    r = max(1, int(release * SR))
    e[:a] = np.linspace(0, 1, a) ** 0.7
    if r < n:
        e[-r:] *= np.linspace(1, 0, r) ** curve
    return e


def glide(n, points):
    """Piecewise linear curve through (fraction, value) points, n samples long."""
    xs = np.linspace(0, 1, n)
    fx, fy = zip(*points)
    return np.interp(xs, fx, fy)


def osc_phase(freq):
    """Phase (radians) for a time-varying frequency array."""
    return 2 * np.pi * np.cumsum(freq) / SR


def pulse_train(freq, rough=0.0, rng=None, harmonics=40):
    """Band-limited glottal-like pulse train (sum of harmonics, 1/k roll-off) with optional jitter."""
    if rough and rng is not None:
        freq = freq * (1 + rough * rng.standard_normal(len(freq)).cumsum() / np.sqrt(np.arange(1, len(freq) + 1)) * 0.02)
    ph = osc_phase(freq)
    out = np.zeros(len(freq))
    nyq = SR / 2
    for k in range(1, harmonics + 1):
        mask = (freq * k) < nyq * 0.9
        out += mask * np.sin(k * ph) / k ** 1.1
    return out / 2.5


def saw(freq, harmonics=30):
    ph = osc_phase(freq)
    out = np.zeros(len(freq))
    for k in range(1, harmonics + 1):
        mask = (freq * k) < SR * 0.45
        out += mask * np.sin(k * ph) / k
    return out * 0.55


def noise(n, rng):
    return rng.standard_normal(n)


def spectral_filter(x, shape):
    """Filters the whole signal with a magnitude response shape(freqs) (zero phase, FFT)."""
    n = len(x)
    size = 1 << (n - 1).bit_length()
    spec = np.fft.rfft(x, size)
    freqs = np.fft.rfftfreq(size, 1 / SR)
    spec *= shape(freqs)
    return np.fft.irfft(spec, size)[:n]


def formants(x, peaks):
    """Vocal tract: sum of resonance peaks [(freq, bandwidth, gain)]."""
    def shape(f):
        out = np.zeros_like(f) + 0.02
        for fc, bw, g in peaks:
            out += g / (1 + ((f - fc) / (bw / 2)) ** 2)
        return out
    return spectral_filter(x, shape)


def lowpass(x, cutoff, order=2):
    return spectral_filter(x, lambda f: 1 / np.sqrt(1 + (f / cutoff) ** (2 * order)))


def highpass(x, cutoff, order=2):
    return spectral_filter(x, lambda f: 1 / np.sqrt(1 + (np.maximum(f, 1) / cutoff) ** (-2 * order)))


def bandpass(x, low, high):
    return highpass(lowpass(x, high), low)


VOWELS = {  # (formant freq, bandwidth, gain)
    'a': [(800, 120, 1.0), (1200, 140, 0.6), (2600, 200, 0.25)],
    'e': [(500, 100, 1.0), (1900, 160, 0.5), (2600, 200, 0.3)],
    'i': [(300, 80, 1.0), (2300, 180, 0.45), (3000, 250, 0.3)],
    'o': [(500, 100, 1.0), (850, 120, 0.6), (2500, 200, 0.15)],
    'u': [(350, 90, 1.0), (700, 120, 0.4), (2400, 200, 0.1)],
    'ah': [(700, 140, 1.0), (1100, 160, 0.7), (2500, 250, 0.3)],
}


def scale_vowel(v, factor):
    return [(f * factor, bw * factor, g) for f, bw, g in VOWELS[v]]


def reverb(x, seconds=1.2, mix=0.25, rng=None, brightness=4000):
    """Convolution with decaying filtered noise (a small hall)."""
    rng = rng or np.random.default_rng(99)
    n = int(seconds * SR)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / (n / 5))
    ir = lowpass(ir, brightness)
    ir[: int(0.012 * SR)] = 0
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    size = 1 << (len(x) + n).bit_length()
    wet = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[: len(x) + n]
    dry = np.concatenate([x, np.zeros(n)])
    return dry * (1 - mix) + wet * mix * 0.6


def soft_clip(x, drive=1.0):
    return np.tanh(x * drive) / np.tanh(drive)


def normalize(x, peak=0.89):
    m = np.max(np.abs(x)) + 1e-9
    return x / m * peak


def trim_tail(x, threshold=1e-3):
    idx = np.nonzero(np.abs(x) > threshold)[0]
    return x[: idx[-1] + int(0.05 * SR)] if len(idx) else x


# ====================================================================== voices

def syllables(rng, count, base_pitch, vowels, formant_scale, rough, length=(0.07, 0.16), gap=(0.01, 0.05), rasp=0.2,
              contour=0.25):
    """Gibberish speech: voiced syllables with random vowels, pitch contours and a breathy rasp."""
    parts = []
    for i in range(count):
        dur = rng.uniform(*length)
        n = int(dur * SR)
        p0 = base_pitch * rng.uniform(0.85, 1.25)
        f = glide(n, [(0, p0), (0.5, p0 * (1 + rng.uniform(-contour, contour))), (1, p0 * rng.uniform(0.8, 1.1))])
        voice = pulse_train(f, rough=rough, rng=rng)
        voice += rasp * noise(n, rng) * 0.4
        v = vowels[rng.integers(len(vowels))]
        s = formants(voice, scale_vowel(v, formant_scale)) * env(n, 0.012, dur * 0.5, 1.5)
        parts.append(s)
        parts.append(np.zeros(int(rng.uniform(*gap) * SR)))
    return np.concatenate(parts)


def goblin(kind):
    """Low and nasty, not squeaky: deep fundamental pitch and a bigger, rougher throat (formant_scale < 1).
    Idle is a mean, guttural "ho ho ho" laugh instead of chittering gibberish."""
    rng = np.random.default_rng({'idle': 11, 'hurt': 12, 'death': 13, 'attack': 14}[kind])
    if kind == 'idle':  # "ho ho ho ho" - descending laugh bursts on a low, rough growl
        parts = []
        beats = rng.integers(3, 6)
        p0 = rng.uniform(95, 115)
        for i in range(beats):
            dur = rng.uniform(0.16, 0.24)
            n = int(dur * SR)
            f = glide(n, [(0, p0 * rng.uniform(0.95, 1.05)), (0.4, p0 * 1.15), (1, p0 * 0.75)])
            voice = pulse_train(f, 1.1, rng, 30) + 0.35 * noise(n, rng)
            s = formants(voice, scale_vowel('o', 0.72)) * env(n, 0.02, dur * 0.55, 1.4)
            parts.append(s * (1 - 0.12 * i))
            parts.append(np.zeros(int(rng.uniform(0.05, 0.09) * SR)))
        x = np.concatenate(parts)
        x = soft_clip(x * 1.6, 1.6)
    elif kind == 'hurt':
        n = int(0.3 * SR)
        f = glide(n, [(0, 240), (0.3, 300), (1, 150)])
        x = formants(pulse_train(f, 1.0, rng) + 0.4 * noise(n, rng), scale_vowel('e', 0.85)) * env(n, 0.005, 0.2)
    elif kind == 'death':
        n = int(1.0 * SR)
        f = glide(n, [(0, 220), (0.2, 260), (1, 85)])
        x = formants(pulse_train(f, 1.4, rng) + 0.5 * noise(n, rng), scale_vowel('a', 0.78)) * env(n, 0.01, 0.65)
    else:  # attack: deep, aggressive roar
        n = int(0.45 * SR)
        f = glide(n, [(0, 130), (0.3, 190), (1, 150)])
        x = formants(pulse_train(f, 1.3, rng) + 0.5 * noise(n, rng), scale_vowel('ah', 0.8)) * env(n, 0.02, 0.22)
        x = soft_clip(x * 2.4, 2.1)
    return reverb(normalize(x), 0.5, 0.15, rng)


def troll(kind):
    rng = np.random.default_rng({'idle': 21, 'hurt': 22, 'death': 23, 'attack': 24}[kind])
    dur = {'idle': 1.4, 'hurt': 0.45, 'death': 2.0, 'attack': 1.0}[kind]
    n = int(dur * SR)
    pts = {'idle': [(0, 70), (0.5, 82), (1, 62)], 'hurt': [(0, 120), (1, 80)], 'death': [(0, 110), (0.3, 95), (1, 40)],
           'attack': [(0, 80), (0.25, 140), (1, 90)]}[kind]
    f = glide(n, pts)
    f *= 1 + 0.05 * np.sin(2 * np.pi * 7 * t_axis(dur)[:n])   # throat flutter
    voice = pulse_train(f, 1.5, rng, harmonics=60) + 0.6 * lowpass(noise(n, rng), 900)
    vowel = {'idle': 'o', 'hurt': 'u', 'death': 'o', 'attack': 'ah'}[kind]
    x = formants(voice, scale_vowel(vowel, 0.62)) * env(n, 0.05 if kind != 'hurt' else 0.01, dur * 0.5)
    x = soft_clip(x * 3, 2.5)
    return reverb(normalize(x), 0.9, 0.2, rng, 2500)


def wolf(kind, variant):
    seed = {'forest': 30, 'shadow': 40, 'frost': 50}[variant] + {'idle': 1, 'hurt': 2, 'death': 3, 'attack': 4}[kind]
    rng = np.random.default_rng(seed)
    if kind == 'idle':        # howl
        dur = 2.2
        n = int(dur * SR)
        f = glide(n, [(0, 380), (0.18, 620), (0.7, 600), (1, 430)])
        f *= 1 + 0.012 * np.sin(2 * np.pi * 5.5 * t_axis(dur)[:n])
        x = formants(pulse_train(f, 0.2, rng, 20), scale_vowel('u', 1.1)) * env(n, 0.25, 0.8)
    elif kind == 'attack':    # snarl
        dur = 0.6
        n = int(dur * SR)
        f = glide(n, [(0, 160), (0.4, 220), (1, 140)])
        x = formants(pulse_train(f, 2.0, rng, 50) + 0.8 * noise(n, rng), scale_vowel('ah', 1.0)) * env(n, 0.01, 0.3)
        x = soft_clip(x * 2.5, 2)
    elif kind == 'hurt':      # yelp
        dur = 0.3
        n = int(dur * SR)
        f = glide(n, [(0, 900), (0.2, 1300), (1, 700)])
        x = formants(pulse_train(f, 0.5, rng, 20), scale_vowel('i', 1.2)) * env(n, 0.005, 0.2)
    else:                     # whine falling
        dur = 1.2
        n = int(dur * SR)
        f = glide(n, [(0, 800), (1, 300)])
        x = formants(pulse_train(f, 0.6, rng, 20), scale_vowel('u', 1.2)) * env(n, 0.02, 0.8)
    if variant == 'shadow':
        x = x + 0.35 * np.concatenate([x[int(0.03 * SR):], np.zeros(int(0.03 * SR))]) * -1   # hollow double voice
        x = lowpass(x, 3000)
    if variant == 'frost':
        c = chimes(rng, len(x) / SR + 0.01, 4)[: len(x)]
        x = x + 0.12 * np.pad(c, (0, len(x) - len(c)))
    return reverb(normalize(x), 1.4 if kind == 'idle' else 0.6, 0.3 if kind == 'idle' else 0.15, rng)


def chimes(rng, seconds, count, base=1800):
    n = int(seconds * SR)
    out = np.zeros(n)
    t = t_axis(seconds)[:n]
    for _ in range(count):
        start = rng.uniform(0, seconds * 0.7)
        f = base * rng.uniform(0.8, 2.2)
        mask = t >= start
        tt = np.maximum(t - start, 0)
        tone = (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 2.76 * tt) + 0.25 * np.sin(2 * np.pi * f * 5.4 * tt))
        out += mask * tone * np.exp(-tt * 5)
    return out / max(1, count) * 0.8


def undead(kind):
    """Low, rasping groans - a decayed throat, not a skeleton's bone rattle. A couple of quiet, deep
    creaks (joints, not clicking teeth) sit far under the voice instead of dominating it."""
    rng = np.random.default_rng({'idle': 61, 'hurt': 62, 'death': 63, 'attack': 64}[kind])
    dur = {'idle': 1.8, 'hurt': 0.45, 'death': 1.9, 'attack': 0.75}[kind]
    n = int(dur * SR)
    out = np.zeros(n)
    pitch = {'idle': [(0, 72), (0.5, 80), (1, 60)], 'hurt': [(0, 130), (0.3, 160), (1, 95)],
             'death': [(0, 95), (0.4, 105), (1, 42)], 'attack': [(0, 85), (0.25, 150), (1, 100)]}[kind]
    vowel = {'idle': 'o', 'hurt': 'e', 'death': 'o', 'attack': 'ah'}[kind]
    f = glide(n, pitch)
    rasp = {'idle': 0.9, 'hurt': 1.1, 'death': 1.3, 'attack': 1.6}[kind]
    voice = pulse_train(f, rasp, rng, 36) * 0.65 + highpass(noise(n, rng), 300) * 0.45
    groan = formants(voice, scale_vowel(vowel, 0.78))
    attack_env = {'idle': 0.3, 'hurt': 0.01, 'death': 0.08, 'attack': 0.015}[kind]
    out += groan * env(n, attack_env, dur * 0.6) * 0.95
    # a slow, throaty wobble - undead don't breathe evenly
    out *= 1 + 0.08 * np.sin(2 * np.pi * {'idle': 2.2, 'hurt': 5, 'death': 1.4, 'attack': 4}[kind] * t_axis(dur)[:n])
    # a few quiet deep creaks (stiff joints), well under the voice - not sharp clicks
    creaks = {'idle': 2, 'hurt': 1, 'death': 3, 'attack': 1}[kind]
    for _ in range(creaks):
        pos = int(rng.uniform(0, dur * 0.85) * SR)
        ln = int(rng.uniform(0.05, 0.1) * SR)
        cf = glide(ln, [(0, rng.uniform(140, 220)), (1, rng.uniform(70, 120))])
        creak = lowpass(pulse_train(cf, 1.8, rng, 8), 500) * np.hanning(ln)
        end = min(n, pos + ln)
        out[pos:end] += creak[: end - pos] * rng.uniform(0.12, 0.22)
    if kind == 'attack':  # a low growl under the yell, not a hiss
        growl = pulse_train(f * 0.5, 1.4, rng, 20) * env(n, 0.02, dur * 0.4) * 0.5
        out += growl
        out = soft_clip(out * 1.8, 1.8)
    return reverb(normalize(out), 1.0, 0.3, rng, 3000)


def wraith(kind, variant='temple'):
    rng = np.random.default_rng({'idle': 71, 'hurt': 72, 'death': 73, 'attack': 74}[kind] + (10 if variant == 'ice' else 0))
    dur = {'idle': 2.4, 'hurt': 0.6, 'death': 2.0, 'attack': 1.0}[kind]
    n = int(dur * SR)
    t = t_axis(dur)[:n]
    # whisper: noise through moving formants
    out = np.zeros(n)
    seg = int(0.12 * SR)
    for i in range(0, n, seg):
        v = ['a', 'e', 'i', 'o', 'u'][rng.integers(5)]
        piece = formants(noise(min(seg, n - i), rng), scale_vowel(v, 1.1))
        w = np.hanning(len(piece) * 2)[: len(piece)] if i == 0 else np.ones(len(piece))
        out[i:i + len(piece)] += piece * w
    out = highpass(out, 600) * 0.6
    # eerie bending tone
    f = glide(n, {'idle': [(0, 620), (0.5, 540), (1, 700)], 'hurt': [(0, 900), (1, 1300)],
                  'death': [(0, 800), (1, 120)], 'attack': [(0, 400), (1, 900)]}[kind])
    tone = np.sin(osc_phase(f)) * 0.35 + np.sin(osc_phase(f * 1.5)) * 0.15
    out = (out + tone) * env(n, 0.3 if kind == 'idle' else 0.03, dur * 0.5)
    out *= 1 + 0.3 * np.sin(2 * np.pi * 3 * t)
    if variant == 'ice':
        out += chimes(rng, dur, 6, 2400)[:n] * 0.4
    if variant == 'void':
        out = out * np.sin(2 * np.pi * 37 * t) * 0.8 + out * 0.4    # ring modulation
    # reversed swell for idle
    if kind == 'idle':
        out = out[::-1] * 0.5 + out * 0.5
    return reverb(normalize(out), 2.0, 0.45, rng, 5000)


def demon(kind, variant='fire'):
    rng = np.random.default_rng({'idle': 81, 'hurt': 82, 'death': 83, 'attack': 84}[kind] + (10 if variant == 'void' else 0))
    dur = {'idle': 1.6, 'hurt': 0.5, 'death': 2.2, 'attack': 0.9}[kind]
    n = int(dur * SR)
    f = glide(n, {'idle': [(0, 95), (0.5, 120), (1, 80)], 'hurt': [(0, 180), (1, 120)], 'death': [(0, 160), (1, 45)],
                  'attack': [(0, 100), (0.3, 190), (1, 110)]}[kind])
    voice = pulse_train(f, 2.5, rng, 60) + 0.7 * noise(n, rng)
    x = formants(voice, scale_vowel('ah', 0.75)) * env(n, 0.04, dur * 0.5)
    x = soft_clip(x * 3, 3)
    # octave-down layer for weight
    sub = np.sin(osc_phase(f / 2)) * env(n, 0.05, dur * 0.5) * 0.4
    x = x + sub
    if variant == 'fire':
        crackle = np.zeros(n)
        for _ in range(int(dur * 40)):
            pos = rng.integers(0, n - 200)
            crackle[pos:pos + 200] += rng.standard_normal(200) * np.exp(-np.arange(200) / 30) * rng.uniform(0.2, 1)
        x += highpass(crackle, 1500) * 0.4
    else:
        t = t_axis(dur)[:n]
        x = x * (0.6 + 0.4 * np.sin(2 * np.pi * 53 * t)) + 0.2 * np.sin(osc_phase(f * 3.01)) * env(n, 0.2, 0.5)
    return reverb(normalize(x), 1.2, 0.25, rng, 3500)


def dragon(kind):
    rng = np.random.default_rng({'idle': 91, 'hurt': 92, 'death': 93, 'attack': 94}[kind])
    dur = {'idle': 2.8, 'hurt': 0.9, 'death': 4.0, 'attack': 2.2}[kind]
    n = int(dur * SR)
    f = glide(n, {'idle': [(0, 60), (0.4, 75), (1, 52)], 'hurt': [(0, 140), (1, 90)], 'death': [(0, 120), (0.4, 100), (1, 30)],
                  'attack': [(0, 55), (0.2, 110), (0.6, 95), (1, 60)]}[kind])
    f *= 1 + 0.06 * np.sin(2 * np.pi * 9 * t_axis(dur)[:n])
    voice = pulse_train(f, 3, rng, 90) + 0.55 * lowpass(noise(n, rng), 2500)
    # formant sweep from "oh" to "aah" - the jaw opens
    a = formants(voice, scale_vowel('o', 0.55))
    b = formants(voice, scale_vowel('ah', 0.6))
    mix = glide(n, [(0, 0), (0.35, 1), (1, 0.7)])
    x = (a * (1 - mix) + b * mix) * env(n, 0.15, dur * 0.45)
    x = lowpass(soft_clip(x * 3, 2.5), 4000)
    x += np.sin(osc_phase(f * 0.5)) * env(n, 0.2, dur * 0.5) * 0.5
    return reverb(normalize(x), 2.5, 0.35, rng, 2500)


def frost_creature(kind):
    """Frost revenants: undead rattle + ice."""
    base = undead(kind)
    rng = np.random.default_rng(55 + len(kind))
    ice = chimes(rng, len(base) / SR + 0.01, 8, 2200)[: len(base)]
    ice = np.pad(ice, (0, len(base) - len(ice)))
    return normalize(base + ice * 0.5)


def golem(kind):
    """Glacier golem: grinding ice and a deep resonant groan."""
    rng = np.random.default_rng({'idle': 101, 'hurt': 102, 'death': 103, 'attack': 104}[kind])
    dur = {'idle': 2.0, 'hurt': 0.6, 'death': 2.6, 'attack': 1.2}[kind]
    n = int(dur * SR)
    grind = bandpass(noise(n, rng), 200, 1800) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 6 * t_axis(dur)[:n])))
    f = glide(n, [(0, 55), (0.5, 48), (1, 40)])
    groan = formants(pulse_train(f, 1, rng, 50), scale_vowel('o', 0.5))
    x = (grind * 0.5 + groan) * env(n, 0.1, dur * 0.5)
    if kind in ('hurt', 'death'):
        x += chimes(rng, dur, 10 if kind == 'death' else 4, 1500)[:n] * 0.6
    return reverb(normalize(lowpass(soft_clip(x * 1.5, 1.5), 3000)), 1.5, 0.3, rng, 3000)


def boss_roar(kind):
    """Generic boss intro roar: dragon voice layered with a low boom."""
    x = dragon('attack')
    rng = np.random.default_rng(200)
    n = len(x)
    t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * (40 + 30 * np.exp(-t * 6)) * t) * np.exp(-t * 2.5)
    return normalize(x + boom * 0.8)


# ====================================================================== music: the guild city theme

NOTE = {'C': -9, 'C#': -8, 'Db': -8, 'D': -7, 'D#': -6, 'Eb': -6, 'E': -5, 'F': -4, 'F#': -3, 'Gb': -3, 'G': -2,
        'G#': -1, 'Ab': -1, 'A': 0, 'A#': 1, 'Bb': 1, 'B': 2}


def hz(name):
    """'D4' -> frequency."""
    pitch, octave = name[:-1], int(name[-1])
    return 440.0 * 2 ** ((NOTE[pitch] + (octave - 4) * 12) / 12)


_CACHE = {}


def cached(fn):
    """Same note, same length -> same samples (the seed comes from the arguments, so it stays deterministic)."""
    def wrapper(freq, dur, rng, *args):
        key = (fn.__name__, round(freq, 2), round(dur, 3)) + args
        if key not in _CACHE:
            seed = zlib.crc32(repr((fn.__name__, int(freq * 100), int(dur * 1000)) + args).encode())
            _CACHE[key] = fn(freq, dur, np.random.default_rng(seed), *args)
        return _CACHE[key]
    return wrapper


@cached
def brass(freq, dur, rng, vel=1.0):
    n = int(dur * SR)
    f = np.full(n, freq) * (1 + 0.004 * np.sin(2 * np.pi * 5 * t_axis(dur)[:n]) * np.linspace(0, 1, n))
    voices = sum(saw(f * d, 24) for d in (1, 1.003, 0.997))
    bright = glide(n, [(0, 0.3), (0.08, 1), (1, 0.7)])
    x = lowpass(voices, 900 + 2200 * vel) * bright
    return x * env(n, 0.06, min(0.3, dur * 0.4), 1.5) * vel


@cached
def strings(freq, dur, rng):
    n = int(dur * SR)
    t = t_axis(dur)[:n]
    out = np.zeros(n)
    for d in (0.994, 0.998, 1.0, 1.002, 1.006):
        vib = 1 + 0.005 * np.sin(2 * np.pi * (5 + rng.uniform(-0.5, 0.5)) * t + rng.uniform(0, 6))
        out += saw(freq * d * vib, 20)
    return lowpass(out / 5, 2500) * env(n, 0.35, 0.5, 1.2)


@cached
def choir(freq, dur, rng, vowel='ah'):
    n = int(dur * SR)
    t = t_axis(dur)[:n]
    out = np.zeros(n)
    for d in (0.996, 1.0, 1.004):
        vib = 1 + 0.006 * np.sin(2 * np.pi * 5.2 * t + rng.uniform(0, 6))
        out += pulse_train(freq * d * vib, 0, None, 30)
    out = formants(out + 0.08 * noise(n, rng), VOWELS[vowel])
    return out * env(n, 0.4, 0.6, 1.2)


def timpani(freq, rng, dur=1.6):
    n = int(dur * SR)
    t = t_axis(dur)[:n]
    f = freq * (1 + 0.15 * np.exp(-t * 30))
    body = np.sin(osc_phase(f)) * np.exp(-t * 3) + 0.5 * np.sin(osc_phase(f * 1.5)) * np.exp(-t * 5)
    hit = lowpass(noise(n, rng), 1500) * np.exp(-t * 40) * 0.6
    return (body + hit) * 0.9


def cymbal(rng, dur=2.5):
    n = int(dur * SR)
    t = t_axis(dur)[:n]
    return lowpass(highpass(noise(n, rng), 6000), 12000) * np.exp(-t * 2.2) * 0.09 * env(n, 0.002, 0.3)


def anvil(rng, dur=0.5, pitch=1.0):
    """A metallic hammer-on-anvil clang: a short noisy strike with a ringing metallic resonance."""
    n = int(dur * SR)
    t = t_axis(dur)[:n]
    strike = highpass(noise(n, rng), 800) * np.exp(-t * 60) * 0.7
    ring = (np.sin(osc_phase(1800 * pitch)) * np.exp(-t * 14) + 0.6 * np.sin(osc_phase(2700 * pitch)) * np.exp(-t * 20)
            + 0.4 * np.sin(osc_phase(4100 * pitch)) * np.exp(-t * 26))
    return (strike + ring * 0.5) * 0.8


def dwarf_theme():
    """About 36 seconds: deep war-drum pulse, anvil-clang rhythm, low brass/choir march - no flutes, no high strings."""
    rng = np.random.default_rng(1309)
    bpm = 76
    beat = 60 / bpm
    total = 36.0
    out = np.zeros(int(total * SR) + SR * 4)

    def put(x, at_beat, gain=1.0):
        i = int(at_beat * beat * SR)
        end = min(len(out), i + len(x))
        out[i:end] += x[: end - i] * gain

    # intro: four slow drum hits, anvil answers each
    for i in range(4):
        put(timpani(hz('D2'), rng, 1.2), i * 2, 0.9)
        put(anvil(rng, 0.4, 0.9), i * 2 + 1, 0.7)
    prog = [('D2', 'A2', 'D3'), ('A#1', 'F2', 'A#2'), ('C2', 'G2', 'C3'), ('D2', 'A2', 'D3'),
            ('G1', 'D2', 'G2'), ('A#1', 'F2', 'A#2'), ('D2', 'A2', 'D3'), ('D2', 'A2', 'D3')]
    for bar, chord in enumerate(prog):
        start = 8 + bar * 4
        # steady war-drum pulse, two per bar, anvil clangs on the offbeat (forge rhythm)
        put(timpani(hz(chord[0]), rng, 1.5), start, 0.75)
        put(timpani(hz(chord[0]), rng, 1.0), start + 2, 0.55)
        put(anvil(rng, 0.35, 0.8 + 0.1 * (bar % 2)), start + 1, 0.55)
        put(anvil(rng, 0.35, 0.8 + 0.1 * (bar % 2)), start + 3, 0.45)
        for note in chord:
            put(strings(hz(note), beat * 4 + 0.3, rng), start, 0.16)
        if bar >= 3:
            put(choir(hz(chord[0]) * 2, beat * 4, rng, 'o'), start, 0.14)
    # low brass march melody, dark and heavy, no instrument above a mid register
    melody = [
        ('D3', 0, 1.5), ('A3', 1.5, 0.5), ('A3', 2, 1), ('C4', 3, 1),
        ('A#3', 4, 1.5), ('A3', 5.5, 0.5), ('G3', 6, 2),
        ('F3', 8, 1), ('G3', 9, 1), ('A3', 10, 1), ('D3', 11, 1),
        ('C3', 12, 1.5), ('D3', 13.5, 0.5), ('D3', 14, 2),
        ('D3', 16, 1), ('F3', 17, 1), ('G3', 18, 2),
        ('A3', 20, 1.5), ('G3', 21.5, 0.5), ('F3', 22, 1), ('D3', 23, 1),
        ('D3', 24, 4),
    ]
    for note, at, length in melody:
        put(brass(hz(note), length * beat + 0.08, rng, 0.75), 8 + at, 0.3)
        put(brass(hz(note) / 2, length * beat + 0.08, rng, 0.6), 8 + at, 0.24)
    # final: anvil flourish and one deep drum hit, no cymbal shimmer (keep it earthbound)
    for k, g in ((33, 0.8), (33.5, 0.6), (34, 0.9)):
        put(anvil(rng, 0.5, 0.85), k, g)
    put(timpani(hz('D2'), rng, 2.2), 34.5, 1.1)
    x = out[: int((8 + 36) * beat * SR) + SR * 2]
    x = reverb(x, 1.8, 0.22, np.random.default_rng(13), 3200)
    x = soft_clip(normalize(x, 0.95) * 1.1, 1.2)
    fade = int(2.0 * SR)
    x[-fade:] *= np.linspace(1, 0, fade) ** 2
    return normalize(trim_tail(x), 0.9)


def guild_theme():
    """About 40 seconds: timpani roll, string swell, heroic brass fanfare over choir, triumphant ending in D major."""
    rng = np.random.default_rng(777)
    bpm = 84
    beat = 60 / bpm
    total = 40.0
    out = np.zeros(int(total * SR) + SR * 4)

    def put(x, at_beat, gain=1.0):
        i = int(at_beat * beat * SR)
        end = min(len(out), i + len(x))
        out[i:end] += x[: end - i] * gain

    # chords: (bar, notes)
    prog = [('D3', 'A3', 'D4', 'F4'), ('A#2', 'F3', 'A#3', 'D4'), ('C3', 'G3', 'C4', 'E4'), ('D3', 'A3', 'D4', 'F4'),
            ('D3', 'A3', 'D4', 'F4'), ('A#2', 'F3', 'A#3', 'D4'), ('F2', 'C3', 'F3', 'A3'), ('C3', 'G3', 'C4', 'E4'),
            ('G2', 'D3', 'G3', 'A#3'), ('A#2', 'F3', 'A#3', 'D4'), ('C3', 'G3', 'C4', 'E4'), ('A2', 'E3', 'A3', 'C#4'),
            ('D3', 'A3', 'D4', 'F#4')]
    # intro: timpani roll crescendo (bar 0) + low string swell
    for i in range(16):
        put(timpani(hz('D2'), rng, 0.8), i * 0.25, 0.15 + 0.5 * i / 16)
    put(strings(hz('D2'), beat * 4, rng), 0, 0.35)
    put(strings(hz('A2'), beat * 4, rng), 0, 0.25)
    put(cymbal(rng), 4, 0.9)
    # body: 12 bars of chords
    for bar, chord in enumerate(prog):
        start = 4 + bar * 4
        length = 4 if bar < len(prog) - 1 else 9
        for note in chord:
            put(strings(hz(note), beat * length + 0.4, rng), start, 0.22)
        put(strings(hz(chord[0][:-1] + str(int(chord[0][-1]) - 1)), beat * length, rng), start, 0.25)  # basses
        if bar >= 4:
            for note in chord[1:3]:
                put(choir(hz(note) * 2 if hz(note) < 300 else hz(note), beat * length, rng, 'ah' if bar % 2 else 'o'), start, 0.16)
        put(timpani(hz(chord[0][:-1] + '2'), rng), start, 0.7)
        if bar % 2 == 1:
            put(timpani(hz(chord[0][:-1] + '2'), rng, 0.8), start + 2.5, 0.35)
            put(timpani(hz(chord[0][:-1] + '2'), rng, 0.8), start + 3, 0.45)
        if bar in (4, 8, 12):
            put(cymbal(rng), start, 0.8)
    # brass fanfare melody (beats from start of bar 1 = beat 4)
    melody = [
        # bar 1-4: call
        ('D4', 0, 1.5), ('A4', 1.5, 0.5), ('A4', 2, 1), ('D5', 3, 1),
        ('C5', 4, 1.5), ('A#4', 5.5, 0.5), ('A4', 6, 2),
        ('G4', 8, 1), ('A4', 9, 0.5), ('A#4', 9.5, 0.5), ('C5', 10, 1), ('E4', 11, 1),
        ('F4', 12, 1.5), ('E4', 13.5, 0.5), ('D4', 14, 2),
        # bar 5-8: answer, higher
        ('D5', 16, 1.5), ('E5', 17.5, 0.5), ('F5', 18, 1), ('D5', 19, 1),
        ('F5', 20, 1.5), ('G5', 21.5, 0.5), ('F5', 22, 1), ('A4', 23, 1),
        ('C5', 24, 1), ('A4', 25, 1), ('F4', 26, 1), ('A4', 27, 1),
        ('G4', 28, 2), ('E4', 30, 1), ('C5', 31, 1),
        # bar 9-12: climb to the climax
        ('A#4', 32, 1), ('D5', 33, 1), ('G5', 34, 2),
        ('F5', 36, 1), ('D5', 37, 1), ('A#4', 38, 1), ('D5', 39, 1),
        ('E5', 40, 1.5), ('F5', 41.5, 0.5), ('G5', 42, 1), ('C5', 43, 1),
        ('C#5', 44, 1), ('E5', 45, 1), ('A5', 46, 2),
        # bar 13: D major - held
        ('F#5', 48, 1), ('A5', 49, 1), ('D6', 50, 6),
    ]
    for note, at, length in melody:
        vel = 0.8 + 0.2 * (at >= 32)
        put(brass(hz(note), length * beat + 0.08, rng, vel), 4 + at, 0.34)
        # horns an octave lower for the second half
        if at >= 16:
            put(brass(hz(note) / 2, length * beat + 0.08, rng, vel * 0.8), 4 + at, 0.22)
    # final hits
    for k, g in ((52, 1.0), (53.5, 0.7), (54, 0.9)):
        put(timpani(hz('D2'), rng, 2.5), k, g)
    put(cymbal(rng, 4), 52, 1.0)
    x = out[: int((4 + 56) * beat * SR) + SR * 2]
    x = reverb(x, 2.8, 0.32, np.random.default_rng(5), 6000)
    x = soft_clip(normalize(x, 0.95) * 1.1, 1.2)
    fade = int(2.5 * SR)
    x[-fade:] *= np.linspace(1, 0, fade) ** 2
    return normalize(trim_tail(x), 0.9)


# ====================================================================== output

def encode(samples, path, quality=4):
    """Writes Ogg Vorbis (mono, 44.1 kHz) bit-exactly via ffmpeg."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    pcm = (np.clip(samples, -1, 1) * 32767).astype('<i2')
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, 'in.wav')
        with wave.open(wav, 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm.tobytes())
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', wav, '-c:a', 'libvorbis', '-q:a', str(quality),
                        '-fflags', '+bitexact', '-flags:a', '+bitexact', '-map_metadata', '-1', path], check=True)


KINDS = ('idle', 'hurt', 'death', 'attack')


def mob_sounds():
    """voice id -> {kind: samples}"""
    voices = {
        'goblin': goblin,
        'troll': troll,
        'wolf': lambda k: wolf(k, 'forest'),
        'shadow_wolf': lambda k: wolf(k, 'shadow'),
        'frost_wolf': lambda k: wolf(k, 'frost'),
        'undead': undead,
        'frost_undead': frost_creature,
        'wraith': lambda k: wraith(k, 'temple'),
        'ice_wraith': lambda k: wraith(k, 'ice'),
        'void_wraith': lambda k: wraith(k, 'void'),
        'demon': lambda k: demon(k, 'fire'),
        'void_demon': lambda k: demon(k, 'void'),
        'dragon': dragon,
        'golem': golem,
    }
    return {v: {k: normalize(trim_tail(fn(k)), 0.85) for k in KINDS} for v, fn in voices.items()}
