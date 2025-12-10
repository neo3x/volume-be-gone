#!/usr/bin/env python3
# Test audio input levels

import sounddevice as sd
import numpy as np
import time

def calculate_db(audio_data):
    # Calculate dB level
    rms = np.sqrt(np.mean(audio_data**2))
    if rms > 0:
        db = 20 * np.log10(rms) + 94
        return db
    return -np.inf

print("Audio Level Monitor")
print("Speak or make noise to see levels")
print("Press Ctrl+C to exit\n")

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    db = calculate_db(indata.flatten())
    if db > -np.inf:
        bar = "=" * int((db + 50) / 2)
        print(f"\rLevel: {db:6.1f} dB [{bar:<50}]", end='')

try:
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=44100):
        while True:
            time.sleep(0.1)
except KeyboardInterrupt:
    print("\n\nTest finished")
