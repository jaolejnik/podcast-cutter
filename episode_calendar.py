import os.path
import twitter
import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/calendar"]


creds = Credentials(token=None,
                    refresh_token=os.getenv("GCALENDAR_REFRESH_TOKEN"),
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=os.getenv("GCALENDAR_CLIENT_ID"),
                    client_secret=os.getenv("GCALENDAR_CLIENT_SECRET"),
                    scopes=SCOPES)
if creds.expired:
    creds.refresh(Request())

service = build('calendar', 'v3', credentials=creds)

now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
events_result = service.events().list(calendarId='primary', timeMin=now,
                                    maxResults=1, singleEvents=True,
                                    orderBy='startTime').execute()
event = events_result.get('items', [])[0]

date_str = event['start']['date']
date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date() 
now = datetime.datetime.now().date()
days_to_episode = (date_obj - now).days

day_word = "dni" if days_to_episode > 1 else "dzień"
when_str = f"za {days_to_episode} {day_word}" if days_to_episode > 0 else "dziś"

message = f"{event['summary']} już {when_str}!"

print(message)
api = twitter.Api(consumer_key=os.environ['CONSUMER_KEY'],
                  consumer_secret=os.environ['CONSUMER_SECRET'],
                  access_token_key=os.environ['ACCESS_TOKEN_KEY'],
                  access_token_secret=os.environ['ACCESS_TOKEN_SECRET'])
status = api.PostUpdate(message)
