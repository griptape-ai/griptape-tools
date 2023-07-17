import logging
import datetime
from schema import Schema, Literal, Optional
from attr import define
from griptape.artifacts import TextArtifact, ErrorArtifact, InfoArtifact
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
            ): str,
            Literal(
                "max_events",
                description="maximum number of events to return"
            ): int
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
                maxResults=values['max_events'], singleEvents=True,
                orderBy='startTime').execute()
            events = events_result.get('items', [])
            return [TextArtifact(str(e)) for e in events]
        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"error retrieving calendar events {e}")

    @activity(config={
        "description": "Can be used to create an event on a google calendar",
        "schema": Schema({
            Literal(
                "calendar_owner_email",
                description="email of the calendar's owner"
            ): str,
            Literal(
                "start_datetime",
                description="combined date-time value in string format according to RFC3399 excluding the timezone for when the meeting starts"
            ): str,
            Literal(
                "start_time_zone",
                description="time zone in which the start time is specified in string format according to IANA time zone data base name, such as 'Europe/Zurich'"
            ): str,
            Literal(
                "end_datetime",
                description="combined date-time value in string format according to RFC3399 excluding the timezone for when the meeting ends"
            ): str,
            Literal(
                "end_time_zone",
                description="time zone in which the end time is specified in string format according to IANA time zone data base name, such as 'Europe/Zurich'"
            ): str,
            Literal(
                "summary",
                description="summary of the event. also used as it's title"
            ): str,
            Literal(
                "description",
                description="description of the event"
            ): str,
            Optional(Literal(
                "location",
                description="location of the event"
            )): str
        })
    })
    def create_event(self, params: dict) -> InfoArtifact | ErrorArtifact:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        values = params['values']
        SCOPES = ['https://www.googleapis.com/auth/calendar']

        try:
            credentials = service_account.Credentials.from_service_account_info(
                self.service_account_credentials, scopes=SCOPES
            )
            delegated_credentials = credentials.with_subject(values["calendar_owner_email"])
            service = build('calendar', 'v3', credentials=delegated_credentials)

            event = {
                'summary': values['summary'],
                'location': values.get('location'),
                'description': values['description'],
                'start': {
                    'dateTime': values['start_datetime'],
                    'timeZone': values['start_time_zone']
                },
                'end': {
                    'dateTime': values['end_datetime'],
                    'timeZone': values['end_time_zone']
                },
                'attendees': [
                    {'email': 'vasily@griptape.ai'},
                    {'email': 'zach@griptape.ai'}
                ]
            }
            event = service.events().insert(calendarId='primary', body=event).execute()
            return InfoArtifact(event.get('htmlLink'))
        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"error creating calendar event: {e}")