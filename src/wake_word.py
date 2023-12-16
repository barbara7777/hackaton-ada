import dotenv
import os

import pvporcupine
import pyaudio
import struct

from agent import init_agent
from speech_core import recognize_from_microphone

if __name__ == "__main__":
    dotenv.load_dotenv()
    
    agent_ex = init_agent()

    porcupine = pvporcupine.create(access_key=os.environ.get('PORCUPINE_KEY'), keywords=["jarvis"])

    pa = pyaudio.PyAudio()

    audio_stream = pa.open(
                    rate=porcupine.sample_rate,
                    channels=1,
                    format=pyaudio.paInt16,
                    input=True,
                    frames_per_buffer=porcupine.frame_length)

    print("[INFO] Listening...")
    while True:
        pcm = audio_stream.read(porcupine.frame_length)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

        keyword_index = porcupine.process(pcm)

        if keyword_index >= 0:
            recognize_from_microphone(agent_ex)