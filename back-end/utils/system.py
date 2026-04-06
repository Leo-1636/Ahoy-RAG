import uuid
import shutil 
from datetime import datetime
from pathlib import Path

def get_uuid() -> str:
    return str(uuid.uuid4())

def get_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
def make_folder(folder_path: Path):
    Path(folder_path).mkdir(parents = True, exist_ok = True)

def move_file(source_path: Path, target_path: Path):
    shutil.move(source_path, target_path)

def copy_file(source_path: Path, target_path: Path):
    shutil.copy(source_path, target_path)
