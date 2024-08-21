from slack_bolt import App
from slack_sdk.errors import SlackApiError
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request, jsonify
import os
import json
from dotenv import load_dotenv, find_dotenv
import vertexai
import time

#import the other files

import gemini
import fish

load_dotenv(find_dotenv())

# API Tokens
SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_BOT_USER_ID = os.getenv('SLACK_BOT_USER_ID')

flask_app = Flask(__name__)
app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)


handler = SlackRequestHandler(app)

# Listener when user Mentions slack bot
@app.event("app_mention")
def event_test(body, say, logger, client):
    logger.info(body)
 

@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)

# handles the request no need to create the challenge parameter SlackRequestHandler does it for you
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

# Listen for the user using the /fish command 
@app.command("/fish")
def pricing_command(ack, say, body,  command, logger, client):
    ack()
    trigger_id = body['trigger_id']
    try:
        # opens the user infterface modals
        with open('fish_class.json') as file:
            json_data = json.load(file)
            client.views_open(trigger_id=trigger_id, view=json_data)
            
    except Exception as e:
                logger.error(f"Error Handling in /modal_example {e}")

# Listens for a callback-id after user submits the /fish  callback_id can be found on file fish_class.json
@app.view("fishy")
def handle_pricing_submission(ack, body, logger, say, client):
    ack()
    try:
        data_bad = body['view']['state']

        # extracts the URI from the the payload
        for k, v in data_bad['values'].items():
            if 'plain_text_input-action' in v and 'value' in v['plain_text_input-action']:
                value = v['plain_text_input-action']['value']

        extract_value = value.split('/')

        # once the URI is found on the payload  check to make sure URI is from google storage
        if extract_value[0] == 'gs:':
            # file_name_name cause fish_name and file_name looks the same

            # file_name_name is the name of the file from the google bucket
            file_name_name = extract_value[-1]

            # activates the gemini AI function and returns a JSON with the list of fish or coral it has identified from the video
            json_data = gemini.gemini_ai(video_uri=value)
            data = json.loads(json_data)
  
            # Downloads the video from the Cloud Bucket
            fish.get_vid_from_bucky(bucket="fish-dataset-test", source=file_name_name, file_name=file_name_name)
            

            for key in data:
                fish_name = key.get("vernacular name").replace(" ", '_')

                # This function will download the frame from the exact timestamp that Gemini classified from the video
                fish.extract_frame_timestamp(timestamp=key.get("timestamp"), video_path=file_name_name, fish_name=fish_name)

                # json payloads text
                text = {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Name:* {key.get("vernacular name")}\n*Scientific Name:* {key.get("scientific name")}\n *Timestamp:* {key.get("timestamp")}"
                    }
                }

                # send the text paylaod to the slack channel
                bob = say(text='post_message_payload', 
                    channel='C07G1AAKXL2', 
                    blocks=[text]
                    )

                # Then uplouds the images from the timestamp of the video to slack
                if bob:
                    client.files_upload_v2(channels='C07G1AAKXL2',  # Specify the channel to upload to
                                        file=f"FRAMES/{fish_name}.jpg",  # Local file path
                                        ) 
                time.sleep(2) 
        else:
            print("Nu uh not from google storage")

    except Exception as e:
        raise e

@app.action('plain_text_input-action')
def handle_action(ack, body, logger):
    ack()
    logger.info(body)

  
if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=5000)

