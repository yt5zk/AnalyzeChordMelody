# modules/audio_processor.py

import librosa
import numpy as np

def load_and_preprocess_audio(file_path, config):
    # サンプリングレートの取得
    sample_rate = config.get('sample_rate', None)
    # オーディオの読み込み
    y, sr = librosa.load(file_path, sr=sample_rate)
    # 正規化
    if config.get('normalize', True):
        y = librosa.util.normalize(y)
    return y, sr