# slack-bot
This script is a Slack bot that listens for mentions in a specific channel. When it is mentioned, it creates a new page in a Notion database with the message text, the user who sent the message, and an image file if it was included.

To use this script, you will need to set the following environment variables:

SLACK_BOT_TOKEN: The token for the Slack bot
SLACK_APP_TOKEN: The token for the Slack app
SLACK_USER_TOKEN: The token for the Slack user
NOTION_KEY: The Notion API key
NOTION_DATABASE_ID: The ID of the Notion database to which the new pages should be added
The script requires the following dependencies:

slack-bolt: A library for building Slack bots
slack-sdk: The Slack API library
notion-client: A library for interacting with the Notion API
dotenv: A library for loading environment variables from a .env file
re: The Python regular expression library
requests: A library for making HTTP requests

To use this script, you will need to create a virtual Python environment and activate it:

python3 -m venv .venv
source .venv/bin/activate
Next, install the required dependencies by running:

Copy code
pip install -r requirements.txt
Once the dependencies are installed, you can run the script:

python3 app.py
