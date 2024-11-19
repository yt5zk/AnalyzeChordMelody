from .base import JudgmentMethod
import numpy as np

class PitchDistributionMethod(JudgmentMethod):
    def analyze_frames(self, valid_frames, pitches, config):
        """
        音域分布に基づくフレーム分析
        """
        # 音域の閾値設定
        low_threshold = config.get('low_pitch_threshold', 48)   # C3
        high_threshold = config.get('high_pitch_threshold', 72) # C5
        
        # 分析用カウンター
        chord_frames = 0
        melody_frames = 0
        frame_types = []
        
        # 音域分布の統計
        range_stats = {
            'low_range_frames': 0,    # 低音域を含むフレーム
            'mid_range_frames': 0,    # 中音域を含むフレーム
            'high_range_frames': 0,   # 高音域を含むフレーム
            'wide_range_frames': 0,   # 広い音域を使用するフレーム
        }
        
        for i in valid_frames:
            frame_pitches = pitches[i]
            active_pitches = frame_pitches[frame_pitches > 0]
            
            if len(active_pitches) > 0:
                # 音域ごとの音符数をカウント
                low_notes = sum(1 for p in active_pitches if p <= low_threshold)
                mid_notes = sum(1 for p in active_pitches if low_threshold < p <= high_threshold)
                high_notes = sum(1 for p in active_pitches if p > high_threshold)
                
                # 音域の使用状況を記録
                if low_notes > 0:
                    range_stats['low_range_frames'] += 1
                if mid_notes > 0:
                    range_stats['mid_range_frames'] += 1
                if high_notes > 0:
                    range_stats['high_range_frames'] += 1
                
                # 広い音域の使用判定
                used_ranges = sum(1 for x in [low_notes, mid_notes, high_notes] if x > 0)
                if used_ranges >= 2:  # 2つ以上の音域を使用
                    range_stats['wide_range_frames'] += 1
                
                # コード判定の条件
                is_chord = (
                    (low_notes > 0 and (mid_notes > 0 or high_notes > 0)) or  # 低音域と他の音域の組み合わせ
                    (len(active_pitches) >= 3 and mid_notes >= 2) or          # 中音域での和音
                    used_ranges >= 2                                          # 広い音域の使用
                )
                
                if is_chord:
                    chord_frames += 1
                    frame_types.append('chord')
                else:
                    melody_frames += 1
                    frame_types.append('melody')
            else:
                melody_frames += 1
                frame_types.append('melody')
        
        stats = {
            'chord_frames': chord_frames,
            'melody_frames': melody_frames,
            **range_stats
        }
        
        return frame_types, stats

    def make_judgment(self, stats, analyzed_frames, config):
        """
        統計情報から最終判定を行う
        """
        if analyzed_frames == 0:
            return 'melody'
        
        # 音域使用率の計算
        wide_range_ratio = stats['wide_range_frames'] / analyzed_frames
        low_range_ratio = stats['low_range_frames'] / analyzed_frames
        
        # 判定閾値
        wide_range_threshold = config.get('wide_range_threshold', 0.15)  # 広い音域使用の閾値
        low_range_threshold = config.get('low_range_threshold', 0.1)    # 低音域使用の閾値
        
        # コード判定条件
        is_chord = (
            wide_range_ratio >= wide_range_threshold or  # 広い音域を一定以上使用
            low_range_ratio >= low_range_threshold       # 低音域を一定以上使用
        )
        
        return 'chord' if is_chord else 'melody' 