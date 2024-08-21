import cv2
from google.cloud import storage
import dropbox
import os
from typing import List
import json
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


# function that download the video from the URI and goes to the folder called FOLDER
def get_vid_from_bucky(bucket, source, file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket)
    blob = bucket.blob(source)

    # blob
    blob.download_to_filename(f"FOLDER/{file_name}")

    print(f"Downloaded storage object {source} from bucket {bucket} to local file {file_name}.")


# given the timestamp we find the FPS of the video so we can find the specific frame from the timestamp
def extract_frame_timestamp(timestamp: str, video_path: str, fish_name: str):

    video = cv2.VideoCapture(f'FOLDER/{video_path}')
    # Gets Frame rate per second
    fps = video.get(cv2.CAP_PROP_FPS)
    timestamp_list  = timestamp.split(':')
    timestamp_list_float = [float(i) for i in timestamp_list]

    minute, seconds = timestamp_list_float

    # frame_name is the frame from the timestamp of the fish or coral
    frame_num = minute * 60 * fps + seconds * fps

    video.set(1, frame_num)

    success, frame = video.read()

    # Outputs the frames to the foldeer called frames
    cv2.imwrite(f'FRAMES/{fish_name}.jpg', frame)

