import imaplib
import logging
import smtplib
from email.mime.text import MIMEText
from typing import Optional
import schema
from attr import define, field
from griptape.artifacts import BaseArtifact, ErrorArtifact, InfoArtifact
from griptape.core import BaseTool
from griptape.core.decorators import activity
from griptape.loaders import TextLoader
from schema import Schema, Literal


@define
class EmailClient(BaseTool):
    # if you set imap|smtp creds explicitly these fields will be overridden
    username: Optional[str] = field(default=None, kw_only=True)
    password: Optional[str] = field(default=None, kw_only=True)

    smtp_host: Optional[str] = field(default=None, kw_only=True)
    smtp_port: Optional[int] = field(default=None, kw_only=True)
    smtp_use_ssl: bool = field(default=True, kw_only=True)

    # if you set the smtp user/password fields they will override
    smtp_user: Optional[str] = field(default=None, kw_only=True)
    smtp_password: Optional[str] = field(default=None, kw_only=True)

    imap_url: Optional[str] = field(default=None, kw_only=True)

    # if you set imap user/password fields they will override
    imap_user: Optional[str] = field(default=None, kw_only=True)
    imap_password: Optional[str] = field(default=None, kw_only=True)

    # be careful of allowing too many records to be returned as it could impact token usage
    email_max_retrieve_count: int = field(default=10, kw_only=True)

    @activity(config={
        "description": "Can be used to retrieve emails",
        "schema": Schema({
            Literal(
                "label",
                description="Label to retrieve emails from such as 'INBOX' or 'SENT'"
            ): str,
            Literal(
                "key",
                description="Key for filtering such as 'FROM' or 'SUBJECT'"
            ): str,
            Literal(
                "search_criteria",
                description="Search criteria to filter emails"
            ): str,
            schema.Optional(
                Literal(
                    "retrieve_count",
                    description="Optional param to override the default max retrieve count"
                )
            ): int
        })
    })
    def retrieve(self, params: dict) -> BaseArtifact:
        values = params["values"]
        imap_url = self.imap_url

        # email username can be overridden by setting the imap user explicitly
        imap_user = self.imap_user
        if imap_user is None:
            imap_user = self.username

        # email password can be overridden by setting the imap password explicitly
        imap_password = self.imap_password
        if imap_password is None:
            imap_password = self.password

        max_retrieve_count = self.email_max_retrieve_count

        label = values["label"]
        key = values["key"]
        search_criteria = values["search_criteria"]

        if "retrieve_count" in values:
            retrieve_count = int(values["retrieve_count"])
        else:
            retrieve_count = max_retrieve_count

        try:
            con = imaplib.IMAP4_SSL(imap_url)
            con.login(imap_user, imap_password)
            con.select(label)

            result, data = con.search(None, key, f'"{search_criteria}"')
            retrieve_list = data[0].split()
            artifact_list = []

            for num in retrieve_list[0:min(int(max_retrieve_count), int(retrieve_count))]:
                typ, data = con.fetch(num, "(RFC822)")

                artifact_list.extend(TextLoader().text_to_artifacts(str(data)))

            con.close()

            return artifact_list
        except Exception as e:
            logging.error(e)

            return ErrorArtifact(f"error retrieving email {e}")

    @activity(config={
        "description": "Can be used to send emails",
        "schema": Schema({
            Literal(
                "to",
                description="Recipient's email address"
            ): str,
            Literal(
                "subject",
                description="Email subject"
            ): str,
            Literal(
                "body",
                description="Email body"
            ): str
        })
    })
    def send(self, params: dict) -> BaseArtifact:
        input_values = params["values"]
        server: Optional[smtplib.SMTP] = None

        # email username can be overridden by setting the smtp user explicitly
        smtp_user = self.smtp_user
        if smtp_user is None:
            smtp_user = self.username

        # email password can be overridden by setting the smtp password explicitly
        smtp_password = self.smtp_password
        if smtp_password is None:
            smtp_password = self.password

        smtp_host = self.smtp_host
        smtp_port = int(self.smtp_port)

        to_email = input_values["to"]
        subject = input_values["subject"]
        msg = MIMEText(input_values["body"])

        try:
            if self.smtp_use_ssl:
                server = smtplib.SMTP_SSL(smtp_host, smtp_port)
            else:
                server = smtplib.SMTP(smtp_host, smtp_port)

            msg["Subject"] = subject
            msg["From"] = smtp_user
            msg["To"] = to_email

            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, [to_email], msg.as_string())

            return InfoArtifact("email was successfully sent")
        except Exception as e:
            logging.error(e)

            return ErrorArtifact(f"error sending email: {e}")
        finally:
            try:
                server.quit()
            except:
                pass
