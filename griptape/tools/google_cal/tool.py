import logging
import datetime
from schema import Schema, Literal
from attr import define
from griptape.artifacts import TextArtifact, ErrorArtifact
from griptape.core.decorators import activity
from griptape.tools import BaseGoogleClient


@define
class GoogleCalClient(BaseGoogleClient):

    @activity(config={
        "description": "Can be used to get upcoming events from a google calendar",
        "schema": Schema({
            Literal(
                "calendar_id",
                description="id of the google calendar such as 'primary'"
            ): str,
            Literal(
                "calendar_owner_email",
                description="email of the calendar's owner"
            ): str
        })
    })
    def get_upcoming_events(self, params: dict) -> list[TextArtifact] | ErrorArtifact:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        values = params["values"]
        SCOPES = ['https://www.googleapis.com/auth/calendar']

        try:
            credentials = service_account.Credentials.from_service_account_info(
                self.service_account_credentials, scopes=SCOPES
            )
            delegated_credentials = credentials.with_subject(values["calendar_owner_email"])
            service = build('calendar', 'v3', credentials=delegated_credentials)
            now = datetime.datetime.utcnow().isoformat() + 'Z'

            events_result = service.events().list(
                calendarId=values["calendar_id"], timeMin=now,
                maxResults=10, singleEvents=True,
                orderBy='startTime').execute()
            events = events_result.get('items', [])
            return [TextArtifact(str(e)) for e in events]
        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"error retrieving calendar events {e}")

    def create_event(self, params: dict) -> TextArtifact | ErrorArtifact:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        values = params["values"]
        SCOPES = ['https://www.googleapis.com/auth/calendar']

        try:
            credentials = service_account.Credentials.from_service_account_info(
                self.service_account_credentials, scopes=SCOPES
            )
            service = build('calendar', 'v3', credentials=credentials)

            event = {
                "summary": values["summary"],
                "location": values["location"],
                "description": values["description"]
            }
            event = service.events().insert(calendarId=values["calendar_id"], body=event).execute()
        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"error creating calendar event: {e}")