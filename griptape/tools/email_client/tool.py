import ast
import logging
import smtplib
import imaplib
from email.mime.text import MIMEText
from typing import Optional
from attr import define, field
from griptape.core import BaseTool, action
from schema import Schema, Literal


@define
class EmailClient(BaseTool):
    # if you set imap|smtp creds explicitly these fields will be overridden
    username: Optional[str] = field(default=None, kw_only=True, metadata={"env": "EMAIL_USERNAME"})
    password: Optional[str] = field(default=None, kw_only=True, metadata={"env": "EMAIL_PASSWORD"})

    smtp_host: Optional[str] = field(default=None, kw_only=True, metadata={"env": "SMTP_HOST"})
    smtp_port: Optional[int] = field(default=None, kw_only=True, metadata={"env": "SMTP_PORT"})
    smtp_from_email: Optional[str] = field(default=None, kw_only=True, metadata={"env": "SMTP_FROM_EMAIL"})
    smtp_use_ssl: bool = field(default=True, kw_only=True, metadata={"env": "SMTP_USE_SSL"})

    # if you set the smtp user/password fields they will override
    smtp_user: Optional[str] = field(default=None, kw_only=True, metadata={"env": "SMTP_USER"})
    smtp_password: Optional[str] = field(default=None, kw_only=True, metadata={"env": "SMTP_PASSWORD"})

    imap_url: Optional[str] = field(default=None, kw_only=True, metadata={"env": "IMAP_URL"})

    # if you set imap user/password fields they will override
    imap_user: Optional[str] = field(default=None, kw_only=True, metadata={"env": "IMAP_USER"})
    imap_password: Optional[str] = field(default=None, kw_only=True, metadata={"env": "IMAP_PASSWORD"})

    # be careful of allowing too many records to be returned as it could impact token usage
    email_max_retrieve_count: int = field(default=10, kw_only=True, metadata={"env": "EMAIL_MAX_RETRIEVE_COUNT"})

    @action(config={
        "name": "retrieve",
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
            Literal(
                "retrieve_count",
                description="Optional param to override the default max retrieve count"
            ): int
        })
    })

    def retrieve(self, value: bytes) -> list[str]:
        params = ast.literal_eval(value.decode())

        imap_url = self.env_value("IMAP_URL")

        # email username can be overridden by setting the imap user explicitly
        imap_user = self.env_value("IMAP_USER")
        if imap_user is None:
            imap_user = self.env_value("EMAIL_USERNAME")

        # email password can be overridden by setting the imap password explicitly
        imap_password = self.env_value("IMAP_PASSWORD")
        if imap_password is None:
            imap_password = self.env_value("EMAIL_PASSWORD")

        max_retrieve_count = self.env_value("EMAIL_MAX_RETRIEVE_COUNT")

        label = params["label"]
        key = params["key"]
        retrieve_count = int(params["retrieve_count"]) if "retrieve_count" in params else max_retrieve_count
        search_criteria = params["search_criteria"]

        try:
            con = imaplib.IMAP4_SSL(imap_url)
            con.login(imap_user, imap_password)
            con.select(label)

            result, data = con.search(None, key, search_criteria)
            retrieve_list = data[0].split()
            messages = []
            for num in retrieve_list[0:min(int(max_retrieve_count), int(retrieve_count))]:
                typ, data = con.fetch(num, '(RFC822)')
                messages.append(data)
            con.close()

            return messages
        except Exception as e:
            logging.error(e)
            return "error retrieving email {e}"


    @action(config={
        "name": "send",
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
    def send(self, value: bytes) -> str:
        server: Optional[smtplib.SMTP] = None
        params = ast.literal_eval(value.decode())

        # email username can be overridden by setting the smtp user explicitly
        smtp_user = self.env_value("SMTP_USER")
        if smtp_user is None:
            smtp_user = self.env_value("EMAIL_USERNAME")

        # email password can be overridden by setting the smtp password explicitly
        smtp_password = self.env_value("SMTP_PASSWORD")
        if smtp_password is None:
            smtp_password = self.env_value("EMAIL_PASSWORD")

        smtp_host = self.env_value("SMTP_HOST")
        smtp_port = int(self.env_value("SMTP_PORT"))
        smtp_from_email = self.env_value("SMTP_FROM_EMAIL")

        to_email = params["to"]
        subject = params["subject"]
        msg = MIMEText(params["body"])

        try:
            if self.env_value("SMTP_USE_SSL"):
                server = smtplib.SMTP_SSL(smtp_host, smtp_port)
            else:
                server = smtplib.SMTP(smtp_host, smtp_port)

            msg["Subject"] = subject
            msg["From"] = smtp_from_email
            msg["To"] = to_email

            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_from_email, [to_email], msg.as_string())

            return "email was successfully sent"
        except Exception as e:
            logging.error(e)

            return f"error sending email: {e}"
        finally:
            try:
                server.quit()
            except:
                pass
