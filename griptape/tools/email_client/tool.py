import json
import smtplib
import ssl
from email.message import EmailMessage
from typing import Optional
from attr import define, field
from griptape.core import BaseTool, action
from schema import Schema, Literal


@define
class EmailClient(BaseTool):
    host: Optional[str] = field(default=None, kw_only=True, metadata={"env": "SMTP_HOST"})
    port: Optional[int] = field(default=None, kw_only=True, metadata={"env": "SMTP_PORT"})
    password: Optional[str] = field(default=None, kw_only=True, metadata={"env": "SMTP_PASSWORD"})
    from_email: Optional[str] = field(default=None, kw_only=True, metadata={"env": "FROM_EMAIL"})
    use_ssl: bool = field(default=True, kw_only=True, metadata={"env": "SMTP_USE_SSL"})

    @action(config={
        "name": "send",
        "description": "Can be used to send emails",
        "value_schema": Schema({
            "value": {
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
            }
        })
    })
    def send(self, value: bytes) -> str:
        server: Optional[smtplib.SMTP] = None
        params = json.loads(value.decode())
        to_email = params["to"]
        subject = params["subject"]
        body = params["body"]
        msg = EmailMessage()

        msg['Subject'] = subject
        msg['From'] = self.env_value("FROM_EMAIL")
        msg['To'] = to_email

        try:
            server = smtplib.SMTP(self.env_value("SMTP_HOST"), int(self.env_value("SMTP_PORT")))

            if self.env_value("SMTP_USE_SSL") == "True":
                server.starttls(context=ssl.create_default_context())

            if self.env_value("SMTP_PASSWORD") != "":
                server.login(self.env_value("FROM_EMAIL"), self.env_value("SMTP_PASSWORD"))

            msg.set_content(body)
            server.send_message(msg)

            return "email was successfully sent"
        except Exception as e:
            return f"error sending email: {e}"
        finally:
            try:
                server.quit()
            except:
                pass
