import ast
import logging
import smtplib
from email.mime.text import MIMEText
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
        params = ast.literal_eval(value.decode())
        host = self.env_value("SMTP_HOST")
        port = int(self.env_value("SMTP_PORT"))
        to_email = params["to"]
        from_email = self.env_value("FROM_EMAIL")
        subject = params["subject"]
        password = self.env_value("SMTP_PASSWORD")
        msg = MIMEText(params["body"])

        try:
            if self.env_value("SMTP_USE_SSL") == "True":
                server = smtplib.SMTP_SSL(host, port)
            else:
                server = smtplib.SMTP(host, port)

            msg["Subject"] = subject
            msg["From"] = from_email
            msg["To"] = to_email

            server.login(from_email, password)
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
