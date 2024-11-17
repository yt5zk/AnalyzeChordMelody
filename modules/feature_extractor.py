# modules/feature_extractor.py

import essentia.standard as ess
import numpy as np

def extract_features(y, sr, config):
    # 多ピッチ推定のパラメータ取得
    hop_size = config.get('hop_size', 512)
    min_frequency = config.get('min_frequency', 50)
    max_frequency = config.get('max_frequency', 5000)

    # 多ピッチ推定器の初期化
    multi_pitch = ess.MultiPitchMelodia(
        hopSize=hop_size,
        sampleRate=sr,
        minFrequency=min_frequency,
        maxFrequency=max_frequency
    )

    # 多ピッチ推定の実行
    pitches = multi_pitch(y)
    return pitches