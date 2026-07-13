import time
import http.client
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import config

RETRIES = 3

def upload_video(youtube, file_path, title, description, tags, privacy_status, publish_at, logger):
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': '22'
        },
        'status': {
            'privacyStatus': privacy_status,
            'selfDeclaredMadeForKids': False
        }
    }
    
    if publish_at and privacy_status == 'private':
        body['status']['publishAt'] = publish_at

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype='video/*')
    request = youtube.videos().insert(part=','.join(body.keys()), body=body, media_body=media)

    response = None
    error = None
    retry = 0
    
    while response is None and retry < RETRIES:
        try:
            status, response = request.next_chunk()
            if status:
                logger.info(f"Uploaded {int(status.progress() * 100)}%")
        except HttpError as e:
            if e.resp.status in [429, 500, 502, 503, 504]:
                logger.warning(f"A retriable HTTP error {e.resp.status} occurred. Retrying...")
                error = e
                time.sleep(2 ** retry)
                retry += 1
            else:
                raise
        except (http.client.HTTPException, ConnectionError) as e:
            logger.warning(f"A retriable network error occurred. Retrying...")
            error = e
            time.sleep(2 ** retry)
            retry += 1

    if response is None:
        raise Exception(f"Failed to upload after {RETRIES} retries. Last error: {error}")
        
    return response.get('id')