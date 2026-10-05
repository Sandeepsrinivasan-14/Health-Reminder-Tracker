"""Outbound notifications: SMS / WhatsApp via Twilio's REST API, and email via SMTP.

Every sender returns a NotificationResult instead of raising, so a missing credential or a
provider outage never crashes an API request. Secrets are never logged.
"""

import logging
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage

import httpx

from ..config import Settings

logger = logging.getLogger(__name__)


@dataclass
class NotificationResult:
    channel: str
    status: str  # sent | failed | not_configured
    detail: str = ""


class Notifier:
    def __init__(self, settings: Settings, http_client: httpx.Client | None = None, smtp_factory=smtplib.SMTP):
        self.settings = settings
        self._http = http_client
        self._smtp_factory = smtp_factory

    def send(self, channel: str, *, to_phone: str | None, to_email: str | None, subject: str, body: str) -> NotificationResult:
        if channel in ("sms", "whatsapp"):
            return self.send_message(channel, to_phone, body)
        if channel == "email":
            return self.send_email(to_email, subject, body)
        return NotificationResult(channel, "failed", f"unknown channel {channel!r}")

    def send_message(self, channel: str, to_phone: str | None, body: str) -> NotificationResult:
        s = self.settings
        if not s.sms_enabled:
            return NotificationResult(channel, "not_configured", "Twilio credentials are not set")
        if not to_phone:
            return NotificationResult(channel, "failed", "no caretaker phone number on the patient profile")

        sender, recipient = s.twilio_from_number, to_phone
        if channel == "whatsapp":
            sender, recipient = f"whatsapp:{sender}", f"whatsapp:{recipient}"

        url = f"https://api.twilio.com/2010-04-01/Accounts/{s.twilio_account_sid}/Messages.json"
        client = self._http or httpx.Client(timeout=15)
        try:
            resp = client.post(
                url, data={"From": sender, "To": recipient, "Body": body}, auth=(s.twilio_account_sid, s.twilio_auth_token)
            )
            if resp.status_code >= 400:
                detail = (
                    resp.json().get("message", resp.text)
                    if resp.headers.get("content-type", "").startswith("application/json")
                    else resp.text
                )
                logger.warning("Twilio rejected %s message: %s", channel, detail)
                return NotificationResult(channel, "failed", str(detail)[:300])
            return NotificationResult(channel, "sent", resp.json().get("sid", ""))
        except httpx.HTTPError as exc:
            logger.warning("Twilio request failed: %s", exc)
            return NotificationResult(channel, "failed", str(exc)[:300])
        finally:
            if self._http is None:
                client.close()

    def send_email(self, to_email: str | None, subject: str, body: str) -> NotificationResult:
        s = self.settings
        if not s.email_enabled:
            return NotificationResult("email", "not_configured", "SMTP credentials are not set")
        if not to_email:
            return NotificationResult("email", "failed", "no caretaker email on the patient profile")

        msg = EmailMessage()
        msg["From"] = s.smtp_from or s.smtp_username
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)
        try:
            with self._smtp_factory(s.smtp_host, s.smtp_port, timeout=15) as server:
                server.starttls()
                server.login(s.smtp_username, s.smtp_password)
                server.send_message(msg)
            return NotificationResult("email", "sent", to_email)
        except (smtplib.SMTPException, OSError) as exc:
            logger.warning("SMTP send failed: %s", exc)
            return NotificationResult("email", "failed", str(exc)[:300])
