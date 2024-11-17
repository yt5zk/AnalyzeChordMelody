# modules/renamer.py

import os

def rename_file(file_path, judgment, logger):
    if judgment == 'chord':
        dir_name, base_name = os.path.split(file_path)
        if '_MLD' in base_name:
            new_base_name = base_name.replace('_MLD', '_CHP')
            new_file_path = os.path.join(dir_name, new_base_name)
            if not os.path.exists(new_file_path):
                os.rename(file_path, new_file_path)
                logger.info(f"Renamed: {file_path} -> {new_file_path}")
            else:
                logger.warning(f"File not renamed to avoid overwrite: {new_file_path}")
        else:
            logger.warning(f"File does not contain '_MLD': {file_path}")
    else:
        logger.info(f"No action taken for: {file_path}")