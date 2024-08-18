import IPython
from dotenv import load_dotenv
import os 
import vertexai
from IPython.display import Markdown, Video, display 
import pandas as pd
from io import StringIO
import json

from vertexai.preview.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmCategory,
    HarmBlockThreshold,
    Part,
    Tool,
    FunctionDeclaration,
)
load_dotenv()

project_id = os.getenv('PROJECT_ID')
location = "us-west1"

vertexai.init(project=project_id, location=location)

model = GenerativeModel("gemini-1.5-pro-001")

safety_settings = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}

instructions = """  
Please return JSON of the vernacular name of the fish and coral species, the scientific name, and the best timestamp of the frame identified from the video. Use this
example following the schema:

    {"vernacular name": str, "scientific name": str, "timestamp": str}

    All fields are required.

               """


video_uri = 'gs://fish-dataset-test/sharktest2.mp4'




def gemini(instructions: str, video_uri: str):

    contents = [
    Part.from_uri(
        uri=video_uri,
        mime_type="video/mp4",
    ),
    instructions
                ]
    generation_config = GenerationConfig(temperature=1, top_p=0.95)
    response = model.generate_content(contents, generation_config=generation_config)

    return response.text.replace('*', '').replace("\n", "").replace('json', "").replace("`", "")




