def two_stage_judgment(valid_frames, pitches, config):
    """
    二段階判定方式
    低音を含む和音フレームと通常の和音フレームを別々に判定
    """
    # 判定用パラメータ
    simultaneous_pitch_threshold = config.get('simultaneous_pitch_threshold', 2)
    low_note_threshold = config.get('low_note_threshold', 48)  # C3以下を低音とみなす
    low_chord_ratio_threshold = config.get('low_chord_ratio_threshold', 0.1)  # 低音和音の判定閾値
    chord_ratio_threshold = config.get('chord_ratio_threshold', 0.2)  # 通常の和音判定閾値
    
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
    
    # 判定（二段階）
    analyzed_frames = len(valid_frames)
    if analyzed_frames == 0:
        return 'melody', frame_types, {
            'chord_frames': 0,
            'melody_frames': 0,
            'low_chord_frames': 0,
            'low_chord_ratio': 0,
            'normal_chord_ratio': 0
        }
    
    low_chord_ratio = low_chord_frames / analyzed_frames
    normal_chord_ratio = chord_frames / analyzed_frames
    
    # 低音和音の比率が一定以上、または通常の和音比率が閾値以上
    is_chord = (low_chord_ratio >= low_chord_ratio_threshold) or \
               (normal_chord_ratio >= chord_ratio_threshold)
    
    stats = {
        'chord_frames': chord_frames,
        'melody_frames': melody_frames,
        'low_chord_frames': low_chord_frames,
        'low_chord_ratio': low_chord_ratio,
        'normal_chord_ratio': normal_chord_ratio
    }
    
    return 'chord' if is_chord else 'melody', frame_types, stats 