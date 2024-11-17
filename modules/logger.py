# modules/logger.py

import logging

def init_logger(config):
    logger = logging.getLogger('AudioAnalysis')
    logger.setLevel(getattr(logging, config['logging_level'].upper(), logging.INFO))

    # コンソールハンドラーの設定
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, config['logging_level'].upper(), logging.INFO))
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ファイルハンドラーの設定
    file_handler = logging.FileHandler('analysis.log')
    file_handler.setLevel(getattr(logging, config['logging_level'].upper(), logging.INFO))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger