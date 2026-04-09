import wave
import struct
import math
import os

def generate_wav(filename, freq_duration_pairs, volume=0.5):
    """
    Generates a simple WAV file using mathematical sine waves.
    Includes a fade-out effect to prevent clicking sounds.
    """
    sample_rate = 44100
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1) # Mono
        wav_file.setsampwidth(2) # 2 bytes per sample (16-bit)
        wav_file.setframerate(sample_rate)
        
        for freq, duration in freq_duration_pairs:
            num_samples = int(duration * sample_rate)
            for i in range(num_samples):
                # Fade out effect for smoother sound
                fade = 1.0 - (i / num_samples)
                value = int(volume * fade * 32767.0 * math.sin(2.0 * math.pi * freq * i / sample_rate))
                
                # Pack the value as a short integer
                data = struct.pack('<h', value)
                wav_file.writeframesraw(data)

    print(f"Created: {filename}")

def main():
    print("Generating game sounds...")
    
    # 1. Beep (Short 440Hz tone)
    generate_wav('assets/sounds/beep.wav', [(440, 0.15)])
    
    # 2. Correct (Happy double tone: C5 then E5)
    generate_wav('assets/sounds/correct.wav', [(523.25, 0.15), (659.25, 0.3)])
    
    # 3. Wrong (Low sad buzz tone)
    generate_wav('assets/sounds/wrong.wav', [(150, 0.4)])
    
    # 4. Time Up (Descending tone)
    generate_wav('assets/sounds/time_up.wav', [(400, 0.2), (300, 0.2), (200, 0.4)])
    
    print("All sounds generated successfully!")

if __name__ == "__main__":
    main()
