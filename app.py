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
    image_files = body['event']['files']
    file_urls = []

    # If there are files in the message
    if image_files:
        # Share the files publicly and get the publicly-shared URLs
        for image_file in image_files:
            file_extension = image_file['filetype']
            file_id = image_file['id']
            file_name = image_file['name']
            response = client.files_sharedPublicURL(file=file_id)
            public_url = response['file']['permalink_public']
            file_urls.append((file_name, public_url))

        # Create a file object in Notion for each file
        files = []
        for file_name, public_url in file_urls:
            file = {
                "type": "external",
                "name": file_name,
                "external": {
                    "url": public_url
                }
            }
            files.append(file)
        new_files = {
            "Files": {
                "files": files
            }
        }

    # Check if the message is a new thread or a reply
    if 'thread_ts' in body['event']:
        # Do nothing if the message is a reply
        return
    else:
        # Get the name of the Slack user who sent the message
        response = client.users_info(user=user)
        slack_user_name = response['user']['name'].title()
        # Use the file urls to specify the "file" property of the database entry
        if image_files:
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
                    "files": files
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

        # Add the new task to the database
        created_page = notion.pages.create(parent={"database_id": NOTION_DATABASE_ID}, properties=new_task)
        # Query the database for the created page using its id
        query_result = notion.databases.query(
            **{
                "database_id": NOTION_DATABASE_ID,
            }
        )
        # Get the URL of the created page
        page_url = query_result["results"][0]["url"]
        # Send a message in Slack to confirm that the QA ticket has been created in Notion
        say({
            "text": "QA ticket created in Notion!",
            "attachments": [
                {
                    "title": "Click here to view ticket",
                    "title_link": page_url
                }
            ]
        })


if __name__ == "__main__":
        handler = SocketModeHandler(app, SLACK_APP_TOKEN)
        handler.start()
