import cv2
from google.cloud import storage
import dropbox
import os
from typing import List
import json
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DROPBOX_TOKEN = os.getenv('DROPBOX_TOKEN')

def upload_to_dropbox(file_path):
    # Create a Dropbox client
    dbx = dropbox.Dropbox(DROPBOX_TOKEN)

 

    try:
        link = dbx.files_get_temporary_link(file_path)
        return link.link
    except dropbox.exceptions.ApiError as e:
        print(f"Error accessing file: {e}")



def get_vid_from_bucky(bucket, source, file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket)
    blob = bucket.blob(source)

    blob.download_to_filename(f"FOLDER/{file_name}")

    print(f"Downloaded storage object {source} from bucket {bucket} to local file {file_name}.")

def extract_frame_timestamp(timestamp: str, video_path: str, fish_name: str):

    video = cv2.VideoCapture(f'FOLDER/{video_path}')
    fps = video.get(cv2.CAP_PROP_FPS)
    timestamp_list  = timestamp.split(':')
    timestamp_list_float = [float(i) for i in timestamp_list]

    minute, seconds = timestamp_list_float

    frame_num = minute * 60 * fps + seconds * fps

    video.set(1, frame_num)

    success, frame = video.read()

    cv2.imwrite(f'FRAMES/{fish_name}.jpg', frame)
#get

def payload_builder(json_data: List[dict], file_name: str) -> json:
    try:
        blocks = []
        print(json_data)
        for key in json_data:
            fish_name = key.get("vernacular name").replace(" ", '_')
            extract_frame_timestamp(timestamp=key.get("timestamp"), video_path=file_name, fish_name=fish_name)
            image_url = upload_to_dropbox(f"FRAMES/{fish_name}")

            text = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Name:* {key.get("vernacular name")}\n*Scientific Name:* {key.get("scientific name")}\n *Timestamp:* {key.get("timestamp")}"
                }
            }
            image = {
                "type": "image",
                "title": {
                    "type": "plain_text",
                    "text": "image1",
                    "emoji": True
                },
                "image_url": f"{image_url}",
                "alt_text": "image1"
            }
            divider = {
                "type": "divider"
            }
            blocks.append(text)
            blocks.append(image)
            blocks.append(divider)
        return blocks
    
    except Exception as e:
        raise e

            


