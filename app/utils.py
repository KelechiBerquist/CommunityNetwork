import os
from typing import Union


def create_dirs(file_path: Union[str, list]):
    file_paths = [file_path] if isinstance(file_path, str) else file_path
    
    for filepath in file_paths:
        try:
            os.makedirs(os.path.dirname(filepath))
        except FileExistsError:
            pass
        except Exception:
            raise
