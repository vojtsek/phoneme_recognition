#! /usr/bin/env python
from IPython.display import display
from alex_asr import Decoder
from alex_asr.utils import lattice_to_nbest
from inreader import InputReader
import wave
import struct
import os
import sys
import logging

# Load speech recognition model from "asr_model_dir" directory.
# decoder = Decoder("tri2b_mmi_b0.05")
# decoder = Decoder(os.path.join(os.path.dirname(__file__), "tri5_nnet2_smbr_ivector_online"))

def join_utterance(decoder, word_ids):
    return (" ".join(map(decoder.get_word, word_ids)))

decoder = Decoder(os.path.join(os.path.dirname(__file__), "tri5"))
AUDIO_FILE = sys.argv[1]
# Load audio frames from input wav file.
data = wave.open(AUDIO_FILE)
frames = data.readframes(data.getnframes())

# Feed the audio data to the decoder.
decoder.accept_audio(frames)
decoder.decode(data.getnframes())
decoder.input_finished()

lkl, lat = decoder.get_lattice()
with open('lattice.dot', 'w') as f:
    f.write(lat.draw())
# Get and print the best hypothesis.
for lik, word_ids in lattice_to_nbest(lat, int(sys.argv[2])):
    print(join_utterance(decoder, word_ids))

prob, word_ids = decoder.get_best_path()
join_utterance(decoder, word_ids)
