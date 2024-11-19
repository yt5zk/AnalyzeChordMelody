# main.py

import sys
import os
from modules.config_loader import load_config
from modules.logger import init_logger
from modules.audio_processor import load_and_preprocess_audio
from modules.feature_extractor import extract_features
from modules.judge import judge_chord_or_melody
from modules.renamer import rename_file

def process_file(file_path, config, logger):
    try:
        # オーディオファイルの読み込みと前処理
        y, sr = load_and_preprocess_audio(file_path, config)
        # 特徴量抽出
        pitches = extract_features(y, sr, config)
        # 判定
        judgment = judge_chord_or_melody(pitches, config)
        # リネーム
        rename_file(file_path, judgment, logger)
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")

def process_file_test_mode(file_path, config, logger):
    try:
        # data_dirからの相対パスを計算
        rel_path = os.path.relpath(file_path, sys.argv[1])
        
        # 相対パスを表示（先頭の改行は削除）
        print(f"{rel_path} | ", end='')
        
        # オーディオファイルの読み込みと前処理
        y, sr = load_and_preprocess_audio(file_path, config)
        # 特徴量抽出
        pitches = extract_features(y, sr, config)
        
        # 判定（結果は関数内で出力）
        judgment = judge_chord_or_melody(y, pitches, config)
        
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")

def sort_files_by_hierarchy(files):
    """
    ファイルパスを階層ごとに昇順でソート
    """
    return sorted(files, key=lambda x: (os.path.dirname(x), os.path.basename(x)))

def find_wav_files(directory):
    """
    指定されたディレクトリから条件に合うWAVファイルを再帰的に探索
    - 拡張子が.wav
    - ファイル名（拡張子を除く）に"_MLD"が含まれる
    """
    wav_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.wav'):
                name_without_ext = os.path.splitext(file)[0]
                if "_MLD" in name_without_ext:
                    wav_files.append(os.path.join(root, file))
    return wav_files

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <directory_path> [--test]")
        sys.exit(1)

    directory_path = sys.argv[1]
    test_mode = "--test" in sys.argv

    if not os.path.isdir(directory_path):
        print("Invalid directory path.")
        sys.exit(1)

    # 設定の読み込み
    config = load_config('config.yaml')
    
    # ロガーの初期化
    logger = init_logger(config)
    
    # 条件に合うファイルを探索
    wav_files = find_wav_files(directory_path)
    
    # ファイルを階層ごとにソート
    sorted_wav_files = sort_files_by_hierarchy(wav_files)
    
    logger.info(f"Found {len(sorted_wav_files)} wav files with '_MLD' in name.")
    logger.info("=" * 80)
    
    if test_mode:
        logger.info("TEST MODE - No files will be renamed")
        logger.info("=" * 80)
        logger.info("")  # 最初の空行
        
        # テストモードでの処理
        for i, file_path in enumerate(sorted_wav_files):
            process_file_test_mode(file_path, config, logger)
            
            # 最後のファイル以外は空行を追加
            if i < len(sorted_wav_files) - 1:
                print()  # ファイル間の空行
    else:
        # 通常モードでの処理
        for file_path in sorted_wav_files:
            process_file(file_path, config, logger)

    logger.info("\n" + "=" * 80)
    logger.info("Processing completed.")

if __name__ == "__main__":
    main()