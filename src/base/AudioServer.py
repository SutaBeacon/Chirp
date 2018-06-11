import pyaudio
import sys
import numpy as np
import aubio

from SafeProcess import SafeProcess


class AudioServer(SafeProcess):

    buffer_size = 1024
    pyaudio_format = pyaudio.paFloat32
    n_channels = 1
    samplerate = 44100
    outputsink = None
    record_duration = None

    tolerance = 0.8
    win_s = 4096 # fft size
    hop_s = buffer_size # hop size


    def setup(self):
        print("*** starting recording")
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.pyaudio_format,
            channels=self.n_channels,
            rate=self.samplerate,
            input=True,
            frames_per_buffer=self.buffer_size)

        self.pitch_o = aubio.pitch("default", self.win_s, self.hop_s, self.samplerate)
        self.pitch_o.set_unit("midi")
        self.pitch_o.set_tolerance(self.tolerance)


    def loop(self):
        try:
            audiobuffer = self.stream.read(self.buffer_size)
            signal = np.fromstring(audiobuffer, dtype=np.float32)

            pitch = self.pitch_o(signal)[0]
            confidence = self.pitch_o.get_confidence()

            print("{} / {}".format(pitch, confidence))

        except KeyboardInterrupt:
            print("*** Ctrl+C pressed, exiting")
            self.terminate()


    def onExit(self):
        print("*** done recording")
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == '__main__':
    audioServer = AudioServer()
    audioServer.start()
    audioServer.join()
