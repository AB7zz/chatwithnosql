from pydub import AudioSegment
from pydub.generators import Sine
import os

def create_test_audio():
    # Create data directory if it doesn't exist
    os.makedirs('data/audio', exist_ok=True)
    
    # Generate a 440 Hz sine wave (A4 note)
    sine_wave = Sine(440)
    
    # Generate 2 seconds of audio
    audio = sine_wave.to_audio_segment(duration=2000)
    
    # Export as WAV
    wav_path = "data/audio/test.wav"
    audio.export(wav_path, format="wav")
    print(f"Created test audio file: {wav_path}")

if __name__ == "__main__":
    create_test_audio()
