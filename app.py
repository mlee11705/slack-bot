from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
from notion_client import Client
from dotenv import load_dotenv
import re
import requests

load_dotenv()
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SLACK_APP_TOKEN = os.environ['SLACK_APP_TOKEN']
SLACK_USER_TOKEN = os.environ['SLACK_USER_TOKEN']
NOTION_KEY = os.environ['NOTION_KEY']
NOTION_DATABASE_ID = os.environ['NOTION_DATABASE_ID']

# Initialize the Notion client
notion = Client(auth=NOTION_KEY)

app = App(token=SLACK_BOT_TOKEN)
client = WebClient(token=SLACK_USER_TOKEN)

@app.event("app_mention")
def mention_handler(body, say, logger):
    # Extract the message text, user who sent the message, and the image file if it exists
    message_text = body['event']['text']
    message_text = re.sub(r"<@U04HUE1GBE0>", "", message_text)
    user = body['event']['user']
    image_file = None
    if 'files' in body['event']:
        image_file = body['event']['files'][0]
        file_extension = image_file['filetype']
        file_id = image_file['id']
        file_name = image_file['name']

        # Share the file publicly and get the publicly-shared URL
        response = client.files_sharedPublicURL(file=file_id)
        public_url = response['file']['permalink_public']

        # Create a file object in Notion
        new_file = {
            "Files": {
                "files": [
                    {
                        "type": "external",
                        "name": file_name,
                        "external": {
                            "url": public_url
                        }
                    }
                ]
            }
        }

    # Check if the message is a new thread or a reply
    if 'thread_ts' in body['event']:
        # Do nothing if the message is a reply
        return
    else:
        # Get the name of the Slack user who sent the message
        response = client.users_info(user=user)
        slack_user_name = response['user']['name']
        # Use the file id to specify the "file" property of the database entry
        if image_file:
            new_task = {
                "title": {
                    "title": [
                        {
                            "text": {
                                "content": message_text
                            }
                        }
                    ]
                },
                "created_by": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": slack_user_name
                            }
                        }
                    ]
                },
                "Files": {
                        "files": [
                            {
                                "type": "external",
                                "name": file_name,
                                "external": {
                                    "url": public_url
                                }
                            }
                        ]
                    }
            }
        else:
            new_task = {
                "title": {
                    "title": [
                        {
                            "text": {
                                "content": message_text
                            }
                        }
                    ]
                },
                "created_by": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": slack_user_name
                            }
                        }
                    ]
                }
            }

        notion.pages.create(parent={"database_id": NOTION_DATABASE_ID}, properties=new_task)

        say({
            "text": "QA ticket created in Notion!"
        })

if __name__ == "__main__":
        handler = SocketModeHandler(app, SLACK_APP_TOKEN)
        handler.start()
