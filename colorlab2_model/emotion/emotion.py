from optparse import OptionParser
from pydub import AudioSegment
from keras.models import load_model
from emotion.utility import globalvars
from emotion.utility.audio import extract

import librosa
import numpy as np
import glob
import pandas as pd
import os
import sys

try:
    import cPickle as pickle
except ImportError:
    import pickle

# TODO: do we have to give model_path as a parameter for 'run()'?
model_path = "emotion/models/LSTM_opensmile_kia_04.h5"

# Please fix this function according to your model. You may need to consider
# preprocessing the wav file.
def run(wav_path):
    global model_path, globalvars
    print("Loading model: ", model_path)
    import pdb; pdb.set_trace()
    model = load_model(model_path)
    y, sr = librosa.load(wav_path, sr=16000)
    wav = AudioSegment.from_file(wav_path)
    f = extract(y, sr)

    u = np.full(
        (f.shape[0], globalvars.nb_attention_param),
        globalvars.attention_init_value,
        dtype=np.float32,
    )

    # input size should be changed.
    f = f[:, :, :36]

    # prediction. this returns a list of softmax values.
    results = model.predict([u, f], batch_size=128, verbose=1)

    return results[0]
