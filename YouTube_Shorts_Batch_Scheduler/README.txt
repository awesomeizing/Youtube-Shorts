YouTube Shorts Batch Auto Uploader (Updated)

CHANGES:
- The application now uploads ALL files in the 'Videos_To_Upload' folder in a single run.
- It no longer sleeps between uploads.
- The first video is published immediately (Public).
- Subsequent videos are uploaded as 'Private' and scheduled (publishAt) exactly 3 hours apart.
- Retains robust duplicate checking, SQLite history, and resumable retries.

RESTART BEHAVIOR:
If you interrupt the program and run it again, it queries the SQLite database to find the latest future scheduled video. It will schedule new queued videos 3 hours AFTER that time. This prevents schedule collisions.

DRY_RUN MODE:
Open `config.py` and set `DRY_RUN = True` to safely view the exact calculated schedule, privacy status, and metadata without contacting YouTube or moving any files. Set to `False` when ready to deploy.