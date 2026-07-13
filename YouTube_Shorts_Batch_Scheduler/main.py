import os
import sys
import shutil
import msvcrt
from datetime import datetime, timedelta, timezone
import config
from utils import setup_logging, get_queued_videos, hash_file, load_metadata
from database import init_db, get_latest_future_schedule, is_duplicate, record_upload
from auth import authenticate_youtube
from uploader import upload_video

def acquire_lock(logger):
    lock_file = open(config.LOCK_FILE, "w")
    try:
        msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
        return lock_file
    except IOError:
        logger.error("Another instance is already running. Exiting.")
        lock_file.close()
        sys.exit(1)
        
def main():
    logger = setup_logging()
    
    # 1. Single Instance Protection
    lock = acquire_lock(logger)
    
    logger.info("Starting YouTube Batch Scheduler Upload...")
    if config.DRY_RUN:
        logger.info("!!! DRY_RUN MODE IS ACTIVE - No files will be moved or uploaded !!!")

    # 2. Authenticate
    youtube = authenticate_youtube()
    if not youtube and not config.DRY_RUN:
        logger.error("Authentication failed.")
        sys.exit(1)

    # 3. Init DB & Metadata
    db_conn = init_db()
    metadata = load_metadata()
    queued_videos = get_queued_videos()

    if not queued_videos:
        logger.info("No videos found in queue. Exiting.")
        return

    # 4. Determine Schedule Base Time
    latest_publish_at = get_latest_future_schedule(db_conn)
    now = datetime.now(timezone.utc)
    
    if latest_publish_at:
        logger.info(f"Existing future schedule found. Resuming schedule after: {latest_publish_at.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    else:
        logger.info("No future schedule found. First video will upload immediately.")

    # 5. Process Queue Sequentially
    for filepath in queued_videos:
        filename = os.path.basename(filepath)
        logger.info(f"--- Processing: {filename} ---")
        
        file_hash = hash_file(filepath)
        if is_duplicate(db_conn, file_hash):
            logger.warning(f"Duplicate detected (Hash: {file_hash}). Skipping {filename}.")
            continue
            
        # Determine schedule for this video
        is_public = False
        if latest_publish_at is None:
            # First upload
            is_public = True
            latest_publish_at = now
            publish_time = now
        else:
            publish_time = latest_publish_at + timedelta(hours=config.SCHEDULE_INTERVAL_HOURS)
            buffer_time = datetime.now(timezone.utc) + timedelta(
                minutes=config.SAFETY_BUFFER_MINUTES
            )
            
            if publish_time < buffer_time:
                publish_time = buffer_time
                
            latest_publish_at = publish_time
            
        publish_at_str = (
            publish_time.astimezone(timezone.utc)
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z")
            if not is_public
            else None
        )
        privacy_status = "private" if not is_public else "public"
        
        # Meta
        meta = metadata.get(filename, {})
        title = meta.get('title', os.path.splitext(filename)[0])
        description = meta.get('description', '')
        tags = [t.strip() for t in meta.get('tags', '').split('|') if t.strip()]
        
        if config.DRY_RUN:
            logger.info(f"[DRY RUN] Planned action for {filename}:")
            logger.info(f"  Title: {title}")
            logger.info(f"  Privacy: {privacy_status}")
            if not is_public:
                logger.info(f"  Scheduled Publish Time (UTC): {publish_at_str}")
            logger.info("-" * 40)
            continue
            
        # Real Upload
        try:
            logger.info(f"Uploading as {privacy_status}" + (f" scheduled at {publish_at_str}" if publish_at_str else " immediately"))
            video_id = upload_video(youtube, filepath, title, description, tags, privacy_status, publish_at_str, logger)
            
            # Post-upload actions
            record_upload(db_conn, filepath, video_id, file_hash, publish_at_str)
            
            # Ensure unique destination filename
            dest_path = os.path.join(config.UPLOADED_DIR, filename)
            counter = 1
            while os.path.exists(dest_path):
                name, ext = os.path.splitext(filename)
                dest_path = os.path.join(config.UPLOADED_DIR, f"{name}_{counter}{ext}")
                counter += 1
                
            shutil.move(filepath, dest_path)
            logger.info(f"Successfully uploaded! Video ID: {video_id}. Moved to {dest_path}")
            
        except Exception as e:
            logger.error(f"Failed to upload {filename}: {e}")
            logger.info("Schedule remains unaffected for subsequent videos.")
            # We do NOT decrement latest_publish_at; the slot is consumed.

    logger.info("Batch run complete.")
    msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
    lock.close()

if __name__ == "__main__":
    main()