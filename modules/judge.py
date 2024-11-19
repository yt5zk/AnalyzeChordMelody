# modules/judge.py

import numpy as np
from .judgment_methods.factory import create_judgment_method

def judge_chord_or_melody(y, pitches, config):
    """
    音声信号全体の判定を行う
    """
    # 判定方式の取得
    method_name = config.get('judgment_method', 'two_stage')
    judgment_method = create_judgment_method(method_name)
    
    # フレームタイプの分析
    frame_types, stats = analyze_frame_types(y, pitches, config, judgment_method)
    
    # 判定
    analyzed_frames = stats['total_frames'] - stats['skip_frames']
    judgment = judgment_method.make_judgment(stats, analyzed_frames, config)
    
    # 結果の出力（シンプルに）
    print(f"{judgment.upper()}")
    print(judgment_method.format_stats(stats, stats['total_frames']))
    
    return judgment

def analyze_frame_types(y, pitches, config, judgment_method):
    """
    フレームごとの分析を行う
    """
    # 音量に基づくフレームの有効性判定
    hop_size = config.get('hop_size', 512)
    min_volume_threshold_db = config.get('min_volume_threshold_db', -24)
    
    # フレームごとの音量を計算
    frame_volumes = []
    max_volume = float('-inf')
    
    for i in range(0, len(y), hop_size):
        frame = y[i:i + hop_size]
        if len(frame) == hop_size:
            volume = 20 * np.log10(np.sqrt(np.mean(frame**2)) + 1e-10)
            frame_volumes.append(volume)
            max_volume = max(max_volume, volume)
    
    # 音量マスクの作成
    volume_mask = np.array(frame_volumes) > min_volume_threshold_db
    total_frames = len(frame_volumes)
    
    # 有効なフレームを抽出
    valid_frames = np.where(volume_mask)[0]
    
    # 判定方式によるフレーム分析
    frame_types, method_stats = judgment_method.analyze_frames(valid_frames, pitches, config)
    
    # 基本統計情報
    stats = {
        'total_frames': total_frames,
        'skip_frames': total_frames - len(valid_frames),
        'max_volume_db': max_volume,
        **method_stats,  # 判定方式固有の統計情報
    }
    
    return frame_types, stats