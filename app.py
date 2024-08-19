from slack_bolt import App
from slack_sdk.errors import SlackApiError
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request, jsonify
import os
import json
from dotenv import load_dotenv, find_dotenv
import vertexai

#import the other files

import gemini
import fish



load_dotenv(find_dotenv())

SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_BOT_USER_ID = os.getenv('SLACK_BOT_USER_ID')

flask_app = Flask(__name__)
app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)


handler = SlackRequestHandler(app)

# listen fur user mentoining the slack app
@app.event("app_mention")
def event_test(body, say, logger):
    logger.info(body)
    say()

@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

    

@app.command("/fish")
def pricing_command(ack, say, body,  command, logger, client):
    ack()
    trigger_id = body['trigger_id']
    try:
        with open('fish_class.json') as file:
            json_data = json.load(file)
            client.views_open(trigger_id=trigger_id, view=json_data)
            
    except Exception as e:
                logger.error(f"Error Handling in /modal_example {e}")

@app.view("fishy")
def handle_pricing_submission(ack, body, logger, say):
    ack()
    try:
        data_bad = body['view']['state']
        for k, v in data_bad['values'].items():
            if 'plain_text_input-action' in v and 'value' in v['plain_text_input-action']:
                value = v['plain_text_input-action']['value']

        extract_value = value.split('/')
        if extract_value[0] == 'gs:':
 
            file_name = extract_value[-1]
            json_data = gemini.gemini_ai(video_uri=value)
            data = json.loads(json_data)
  
            fish.get_vid_from_bucky(bucket="fish-dataset-test", source=file_name, file_name=file_name)
            blocks = fish.payload_builder(json_data=data, file_name=file_name)

            say(text='post_message_payload', 
                                     channel='C07G1AAKXL2', 
                                     blocks=blocks
                                    )
  
            


        
        else:
            pass

    except Exception as e:
        raise e

@app.action('plain_text_input-action')
def handle_action(ack, body, logger):
    ack()
    logger.info(body)

  
if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=5000)

