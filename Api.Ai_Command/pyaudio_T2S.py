#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import pyttsx
engine = pyttsx.init()

try:
    import apiai
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
    import apiai


import thread
import pyaudio
import time

CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 2

CLIENT_ACCESS_TOKEN = 'c5df268ba54143e28e73bee32c162ffd'

def input_thread(L):
    raw_input()
    L.append(None)

def main():
    resampler = apiai.Resampler(source_samplerate=RATE)

    vad = apiai.VAD()

    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

    request = ai.voice_request()

    request.lang = 'en' # optional, default value equal 'en'

    def callback(in_data, frame_count, time_info, status):
        frames, data = resampler.resample(in_data, frame_count)
        state = vad.processFrame(frames)
        request.send(data)

        if (state == 1):
            return in_data, pyaudio.paContinue
        else:
            return in_data, pyaudio.paComplete

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS, 
                    rate=RATE, 
                    input=True,
                    output=False,
                    frames_per_buffer=CHUNK,
                    stream_callback=callback)

    stream.start_stream()

    print ("Say! Press enter for stop audio recording.")

    try:
        L = []
        thread.start_new_thread(input_thread, (L,))

        while stream.is_active() and len(L) == 0:
            time.sleep(0.1)
            
    except Exception:
        raise e
    except KeyboardInterrupt:
        pass

    stream.stop_stream()
    stream.close()
    p.terminate()

    print ("Wait for response...")
    response = request.getresponse()

    x=response.read()
    #parser de jsond
    jeyson=json.loads(x)

    #print (type(x))
    print (x)    
    #print (jeyson['id'])
    print (jeyson['result']['resolvedQuery'])
    print("\n---------")
    print( jeyson['result']['fulfillment']['speech'])
    #print( jeyson['result']['fulfillment'])

    to_say=jeyson['result']['fulfillment']['speech']

    if to_say=="":
        engine.say("I dont undestand you,can you repeat it!")
        print("no response from agent")
    else:
        engine.say(to_say)
        engine.say('ok human')
    
    
    engine.runAndWait() 


if __name__ == '__main__':
    main()
