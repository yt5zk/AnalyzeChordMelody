class JudgmentMethod:
    """
    判定方式の基本クラス
    全ての判定方式はこのクラスを継承する
    """
    def analyze_frames(self, valid_frames, pitches, config):
        """
        フレーム分析を行う
        Returns:
            tuple: (frame_types, stats)
        """
        raise NotImplementedError
        
    def make_judgment(self, stats, analyzed_frames, config):
        """
        統計情報から最終判定を行う
        Returns:
            str: 'chord' or 'melody'
        """
        raise NotImplementedError
        
    def format_stats(self, stats, total_frames):
        """
        統計情報を文字列にフォーマット
        """
        analyzed_frames = total_frames - stats['skip_frames']
        active_frame_ratio = (analyzed_frames / total_frames) * 100
        
        # 基本的な統計情報
        output = [
            f"Max Frame Volume: {stats['max_volume_db']:.1f}dB",
            f"Analyzed Frames: {analyzed_frames} ({active_frame_ratio:.1f}% of total)",
            f"- Skipped: {stats['skip_frames']:3d} ({stats['skip_frames']/total_frames*100:5.1f}%)",
            f"- Chord:   {stats['chord_frames']:3d} ({stats['chord_frames']/total_frames*100:5.1f}%)",
            f"- Melody:  {stats['melody_frames']:3d} ({stats['melody_frames']/total_frames*100:5.1f}%)"
        ]
        
        return "\n".join(output)