from .base import JudgmentMethod

class TwoStageMethod(JudgmentMethod):
    def analyze_frames(self, valid_frames, pitches, config):
        """
        二段階判定方式による分析
        """
        # 判定用パラメータ
        simultaneous_pitch_threshold = config.get('simultaneous_pitch_threshold', 2)
        low_note_threshold = config.get('low_note_threshold', 48)  # C3以下を低音とみなす
        
        # カウンター初期化
        chord_frames = 0
        melody_frames = 0
        low_chord_frames = 0
        
        # フレーム分析
        frame_types = []
        for i in valid_frames:
            frame_pitches = pitches[i]
            active_pitches = frame_pitches[frame_pitches > 0]
            
            if len(active_pitches) >= simultaneous_pitch_threshold:
                # 通常の和音判定
                chord_frames += 1
                frame_types.append('chord')
                
                # 低音を含む和音かチェック
                has_low_note = any(pitch <= low_note_threshold for pitch in active_pitches)
                if has_low_note:
                    low_chord_frames += 1
            else:
                melody_frames += 1
                frame_types.append('melody')
        
        # 統計情報に必要な比率を追加
        stats = {
            'chord_frames': chord_frames,
            'melody_frames': melody_frames,
            'low_chord_frames': low_chord_frames,
            'low_chord_ratio': low_chord_frames / len(valid_frames) if len(valid_frames) > 0 else 0,
            'normal_chord_ratio': chord_frames / len(valid_frames) if len(valid_frames) > 0 else 0
        }
        
        return frame_types, stats

    def make_judgment(self, stats, analyzed_frames, config):
        """
        統計情報から最終判定を行う
        """
        if analyzed_frames == 0:
            return 'melody'
            
        low_chord_ratio = stats['low_chord_frames'] / analyzed_frames
        normal_chord_ratio = stats['chord_frames'] / analyzed_frames
        
        # 判定閾値
        low_chord_ratio_threshold = config.get('low_chord_ratio_threshold', 0.1)
        chord_ratio_threshold = config.get('chord_ratio_threshold', 0.2)
        
        # 低音和音の比率が一定以上、または通常の和音比率が閾値以上
        is_chord = (low_chord_ratio >= low_chord_ratio_threshold) or \
                   (normal_chord_ratio >= chord_ratio_threshold)
                   
        return 'chord' if is_chord else 'melody' 

    def format_stats(self, stats, total_frames):
        # 基本的な統計情報を取得
        base_stats = super().format_stats(stats, total_frames)
        
        # 二段階判定方式固有の統計情報を追加
        additional_stats = [
            f"Low Chord Ratio: {stats['low_chord_ratio']*100:.1f}%",
            f"Normal Chord Ratio: {stats['normal_chord_ratio']*100:.1f}%"
        ]
        
        return base_stats + "\n" + "\n".join(additional_stats) 