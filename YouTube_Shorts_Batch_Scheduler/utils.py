import os
import re
import csv
import hashlib
import logging
from logging.handlers import RotatingFileHandler
import config

def setup_logging():
    logger = logging.getLogger("YouTubeUploader")
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(config.LOG_FILE, maxBytes=5*1024*1024, backupCount=2, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(handler)
        
    # Also log to console
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)
    return logger

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def get_queued_videos():
    files = [f for f in os.listdir(config.VIDEOS_DIR) if f.lower().endswith(('.mp4', '.mov', '.mkv'))]
    files.sort(key=natural_sort_key)
    return [os.path.join(config.VIDEOS_DIR, f) for f in files]

def hash_file(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()

def load_metadata():
    metadata = {}
    if os.path.exists(config.METADATA_FILE):
        with open(config.METADATA_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                filename = row.get('filename', '').strip()
                if filename:
                    metadata[filename] = row
    return metadata