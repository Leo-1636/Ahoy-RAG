import math
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

def get_page_number(source_path: Path) -> int:
    result = subprocess.run(
        ["pdfinfo", str(source_path)],
        capture_output = True, text = True, check = True
    )
    for line in result.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":")[1].strip())
    return 0

def convert_image(source_path: Path, target_path: Path, start_page: int, end_page: int):
    subprocess.run([
        "pdftoppm", "-png", 
        "-r", "400", 
        "-scale-to", "2048", 
        "-f", str(start_page),
        "-l", str(end_page),    
        source_path, target_path
    ], check = True)

def convert_images(source_path: Path, target_path: Path, page_number: int, threads: int = 24):
    page_per_thread = math.ceil(page_number / threads)
    with ThreadPoolExecutor(max_workers = threads) as executor:
        for start_page in range(1, page_number + 1, page_per_thread):
            end_page = min(start_page + page_per_thread - 1, page_number)
            executor.submit(convert_image, source_path, target_path, start_page, end_page)
