import aiosmtplib
from email.message import EmailMessage


async def send_email(receiver, content):

    msg = EmailMessage()

    msg["From"] = "organizer@eventos.ai"
    msg["To"] = receiver
    msg["Subject"] = "Event Invitation"

    msg.set_content(content)

    await aiosmtplib.send(
        msg,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
    )