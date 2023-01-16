import requests
import maya
import datetime
from os import environ
from typing import Optional, List
from dotenv import load_dotenv
load_dotenv()

def get_figma_file_name(file_key:str) -> Optional[List[str]]:
  """Retrieves file name of figma file"""

  FIGMA_PERSONAL_ACCESS_TOKEN = environ.get('FIGMA_PERSONAL_ACCESS_TOKEN')
  FIGMA_API_URL = f"https://api.figma.com/v1/files/{file_key}"
  FIGMA_API_HEADERS = { 'X-FIGMA-TOKEN': FIGMA_PERSONAL_ACCESS_TOKEN }

  r = requests.get(url = FIGMA_API_URL, headers = FIGMA_API_HEADERS)
  data = r.json()

  return data["name"]

def get_figma_file_updates(file_key:str) -> Optional[List[str]]:
  """Retrieves formatted message containing updates for the file"""

  FIGMA_PERSONAL_ACCESS_TOKEN = environ.get('FIGMA_PERSONAL_ACCESS_TOKEN')
  FIGMA_API_URL = f"https://api.figma.com/v1/files/{file_key}/versions"
  FIGMA_API_HEADERS = { 'X-FIGMA-TOKEN': FIGMA_PERSONAL_ACCESS_TOKEN }

  r = requests.get(url = FIGMA_API_URL, headers = FIGMA_API_HEADERS)
  data = r.json()
  versions = data["versions"]

  filter_function = lambda x: maya.parse(
      x['created_at']).datetime().date() == datetime.date.today() and x['description'] is not None and len(x['description']
    ) > 0
  todays_versions = list(filter(filter_function, versions))

  updates = []
  for version in todays_versions:
    if version['description']:
      updates.append(version['description'])

  return updates
  
def post_message(message:str) -> None:
  """Post message to slack"""

  DEBUG_MODE = environ.get('DEBUG_MODE', "0")
  if DEBUG_MODE != "0":
    return

  return
  SLACK_TEAM_ID = environ.get('SLACK_TEAM_ID')
  SLACK_USER_ID = environ.get('SLACK_USER_ID')
  SLACK_CHANNEL_ID = environ.get('SLACK_CHANNEL_ID')
  SLACK_API_URL = "https://hooks.slack.com/services/" + SLACK_TEAM_ID + "/" + SLACK_USER_ID + "/" + SLACK_CHANNEL_ID

  # TODO: Try making the message better formatted
  # https://api.slack.com/messaging/composing/layouts#adding-blocks
  data = {"text": message}
  r = requests.post(url = SLACK_API_URL, json = data)

def slack_updates_for_figma_files() -> None:
  """Retrieves new updates figma files and posts to a slack channel"""
  
  FIGMA_FILE_KEY = environ.get('FIGMA_FILE_KEY')
  FIGMA_FILE_KEYS = environ.get('FIGMA_FILE_KEYS', "")
  
  file_keys = FIGMA_FILE_KEYS.split(',')

  if FIGMA_FILE_KEY:
    file_keys = [FIGMA_FILE_KEY]

  message = ""
  number_of_files = len(file_keys)
  current_file = 1
  for file_key in file_keys:
    print(f'Retrieving file info {current_file}/{number_of_files}')

    file_name = get_figma_file_name(file_key=file_key)
    file_updates = get_figma_file_updates(file_key=file_key)

    if file_updates:
      message += f"\n{file_name}"
      for file_update in file_updates:
        message += f"\n{file_update}"
      message += "\n"

    current_file +=1
  
  if message:
    print("\n Sending following message to slack: ")
    # The period is so that the message starts in the new line, this is because
    # slack removes new lines at the start of a message
    message = "." + message
    print(message)
    post_message(message)
