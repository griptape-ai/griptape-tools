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
    smtp_host: Optional[str] = field(default=None, kw_only=True, metadata={"env": "SMTP_HOST"})
    smtp_port: Optional[int] = field(default=None, kw_only=True, metadata={"env": "SMTP_PORT"})
    smtp_password: Optional[str] = field(default=None, kw_only=True, metadata={"env": "SMTP_PASSWORD"})
    from_email: Optional[str] = field(default=None, kw_only=True, metadata={"env": "FROM_EMAIL"})
    smtp_use_ssl: bool = field(default=True, kw_only=True, metadata={"env": "SMTP_USE_SSL"})

    imap_url: Optional[str] = field(default=None, kw_only=True, metadata={"env": "IMAP_URL"})
    imap_user: Optional[str] = field(default=None, kw_only=True, metadata={"env": "IMAP_USER"})
    imap_password: Optional[str] = field(default=None, kw_only=True, metadata={"env": "IMAP_PASSWORD"})

    @action(config={
        "name": "retrieve",
        "description": "Can be used to retrieve emails",
        "value_schema": Schema({
            "value": {
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
                ): str
            }
        })
    })

    def retrieve(self, value: bytes) -> str:
        con: Optional[imaplib.IMAP4_SSL] = None
        params = ast.literal_eval(value.decode())
        imap_url = self.env_value("IMAP_URL")
        imap_user = self.env_value("IMAP_USER")
        imap_password = self.env_value("IMAP_PASSWORD")
        label = params["label"]
        key = params["key"]
        search_criteria = params["search_criteria"]

        try:
            con = imaplib.IMAP4_SSL(imap_url)
            con.login(imap_user, imap_password)
            con.select(label)

            result, data = con.search(None, key, search_criteria)
            messages = []
            for num in data[0].split():
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
        smtp_host = self.env_value("SMTP_HOST")
        smtp_port = int(self.env_value("SMTP_PORT"))
        to_email = params["to"]
        from_email = self.env_value("FROM_EMAIL")
        subject = params["subject"]
        smtp_password = self.env_value("SMTP_PASSWORD")
        msg = MIMEText(params["body"])

        try:
            if self.env_value("SMTP_USE_SSL") == "True":
                server = smtplib.SMTP_SSL(smtp_host, smtp_port)
            else:
                server = smtplib.SMTP(smtp_host, smtp_port)

            msg["Subject"] = subject
            msg["From"] = from_email
            msg["To"] = to_email

            server.login(from_email, smtp_password)
            server.sendmail(from_email, [to_email], msg.as_string())

            return "email was successfully sent"
        except Exception as e:
            logging.error(e)

            return f"error sending email: {e}"
        finally:
            try:
                server.quit()
            except:
                pass
