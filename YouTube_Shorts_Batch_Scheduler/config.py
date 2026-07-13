import os

# ---------------------------------------------------------
# SCHEDULING & RUN MODE
# ---------------------------------------------------------
DRY_RUN = False                # Set to False to perform real uploads and modifications
SCHEDULE_INTERVAL_HOURS = 3   # Hours between each scheduled upload
SAFETY_BUFFER_MINUTES = 10    # Minimum future time buffer for scheduled publishAt

# ---------------------------------------------------------
# DIRECTORIES & FILES
# ---------------------------------------------------------
VIDEOS_DIR = "Videos_To_Upload"
UPLOADED_DIR = "Uploaded"
CLIENT_SECRETS_FILE = "client_secret.json"
TOKEN_FILE = "token.json"
METADATA_FILE = "metadata.csv"
DB_FILE = "upload_history.db"
LOG_FILE = "uploader.log"
LOCK_FILE = "uploader.lock"

# Ensure directories exist
os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(UPLOADED_DIR, exist_ok=True)