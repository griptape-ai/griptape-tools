import logging
import base64
from email.message import EmailMessage
from schema import Schema, Literal
from attr import define
from griptape.artifacts import TextArtifact, ErrorArtifact
from griptape.core.decorators import activity
from griptape.tools import BaseGoogleClient
from google.oauth2 import service_account
from googleapiclient.discovery import build

@define
class GoogleGmailClient(BaseGoogleClient):

    @activity(config={
        "description" : "Can be used to create a draft email in GMail",
        "schema" : Schema({
            Literal(
                "to",
                description="email address which to send to"
            ): str,
            Literal(
                "subject",
                description="subject of the email"
            ): str,
            Literal(
                "from",
                description="email address which to send from"
            ): str,
            Literal(
                "body",
                description="body of the email"
            ): str,
            Literal(
                "inbox_owner",
                description="email address of the inbox owner where the draft will be created. if not provided, use the from address"
            ): str
        })
    })
    def create_draft_email(self, params: dict) -> TextArtifact | ErrorArtifact:
        values = params["values"]
        SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.service_account_credentials_path, scopes=SCOPES
            )

            # TODO: test if this works for same user (non service account)
            delegated_creds = credentials.with_subject(values["inbox_owner"])
            service = build('gmail', 'v1', credentials=delegated_creds)

            message = EmailMessage()
            message.set_content(values["body"])
            message['To'] = values["to"]
            message['From'] = values["from"]
            message['Subject'] = values["subject"]

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {
                'message': {
                    'raw': encoded_message
                }
            }
            draft = service.users().drafts().create(userId='me', body=create_message).execute()
            return TextArtifact(f'Draft Id: {draft["id"]}')

        except Exception as error:
            logging.error(error)
            return ErrorArtifact(f'Error creating draft email: {error}')


