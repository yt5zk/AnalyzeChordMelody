# modules/judge.py

import numpy as np
import librosa
from . import judge_methods

def calculate_frame_rms(frame):
    """フレームのRMS値をdBで返す"""
    rms = np.sqrt(np.mean(np.square(frame)))
    return 20 * np.log10(rms) if rms > 0 else -float('inf')

def get_pitch_weight(midi_note, config):
    """
    MIDIノートナンバーに基づいて重みを計算
    high_weight/low_weightを使用して重みづけを調整
    """
    weight_config = config.get('pitch_weight', {})
    base_note = weight_config.get('base_note', 60)      # C4
    high_weight = weight_config.get('high_weight', 0.7) # 高音域の重み
    low_weight = weight_config.get('low_weight', 1.5)   # 低音域の重み
    low_rate = weight_config.get('low_rate', 0.02)      # 低音域の増加率
    high_rate = weight_config.get('high_rate', 0.02)    # 高音域の減少率
    
    if midi_note <= base_note:
        # 低音域は重みを増加
        weight = 1.0 + min(low_weight - 1.0, (base_note - midi_note) * low_rate)
    else:
        # 高音域は重みを減少
        weight = 1.0 - min(1.0 - high_weight, (midi_note - base_note) * high_rate)
    return weight

def analyze_frame_types(y, pitches, config):
    """
    音声信号とピッチ情報からフレームタイプを判定
    """
    hop_size = config.get('hop_size', 512)
    min_volume_threshold_db = config.get('min_volume_threshold_db', -24)
    max_volume_threshold_db = config.get('max_volume_threshold_db', -12)
    
    # HPSSのパラメータを最適化
    harmonic, _ = librosa.effects.hpss(
        y,
        kernel_size=31,
        power=2.0,
        mask=False,
        margin=1.0
    )
    
    # フレーム分割
    frames = librosa.util.frame(
        harmonic,
        frame_length=hop_size,
        hop_length=hop_size,
        axis=0
    )
    
    # 一括でRMS値を計算
    rms = np.sqrt(np.mean(np.square(frames), axis=1))
    frame_rms_values = 20 * np.log10(np.maximum(rms, 1e-10))
    
    # 有効な最大音量を取得
    valid_volumes = frame_rms_values[frame_rms_values != float('-inf')]
    max_volume_db = np.max(valid_volumes) if len(valid_volumes) > 0 else -float('inf')
    
    total_frames = len(frames)
    frame_types = np.full(total_frames, 'melody', dtype=object)
    
    # 音量による判定（ベクトル化）
    volume_mask = (frame_rms_values > min_volume_threshold_db) & \
                 (frame_rms_values < max_volume_threshold_db) & \
                 (frame_rms_values != float('-inf'))
    
    # 有効なフレームを抽出
    valid_frames = np.where(volume_mask)[0]
    skip_frames = total_frames - len(valid_frames)
    
    # 判定方法の選択
    judgment_method = config.get('judgment_method', 'two_stage')  # デフォルトは二段階判定
    
    if judgment_method == 'two_stage':
        judgment, frame_types, method_stats = judge_methods.two_stage_judgment(
            valid_frames, pitches, config)
    else:
        raise ValueError(f"Unknown judgment method: {judgment_method}")
    
    # 統計情報の作成
    stats = {
        'total_frames': total_frames,
        'skip_frames': skip_frames,
        'max_volume_db': max_volume_db,
        **method_stats  # 判定方法固有の統計情報を追加
    }
    
    return frame_types, stats

def judge_chord_or_melody(y, pitches, config):
    """
    音声信号全体の判定を行う
    """
    y_normalized = librosa.util.normalize(y)
    frame_types, stats = analyze_frame_types(y_normalized, pitches, config)
    
    # 判定対象フレーム（skip以外）を抽出
    analyzed_frames = stats['total_frames'] - stats['skip_frames']
    active_frame_ratio = (analyzed_frames / stats['total_frames']) * 100
    
    # 二段階判定による最終判定
    if config.get('judgment_method', 'two_stage') == 'two_stage':
        # 低音和音の比率または通常の和音比率で判定
        is_chord = (stats['low_chord_ratio'] >= config.get('low_chord_ratio_threshold', 0.1)) or \
                  (stats['normal_chord_ratio'] >= config.get('chord_ratio_threshold', 0.2))
        judgment = 'CHORD' if is_chord else 'MELODY'
        
        # 判定結果を出力
        print(f"{judgment}")
        print(f"""Max Frame Volume: {stats['max_volume_db']:.1f}dB
Analyzed Frames: {analyzed_frames} ({active_frame_ratio:.1f}% of total)
- Skipped: {stats['skip_frames']:3d} ({stats['skip_frames']/stats['total_frames']*100:5.1f}%)
- Chord:   {stats['chord_frames']:3d} ({stats['chord_frames']/stats['total_frames']*100:5.1f}%)
- Melody:  {stats['melody_frames']:3d} ({stats['melody_frames']/stats['total_frames']*100:5.1f}%)
Low Chord Ratio: {stats['low_chord_ratio']*100:.1f}%
Normal Chord Ratio: {stats['normal_chord_ratio']*100:.1f}%""")
        
        return judgment.lower()
    
    return 'melody'  # デフォルト値