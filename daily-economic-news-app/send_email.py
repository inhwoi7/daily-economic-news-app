import os
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import Optional

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def get_gmail_service():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # The 'credentials.json' file must be downloaded from Google Cloud Console
            # and placed in the project root directory.
            if not os.path.exists("credentials.json"):
                print("Error: credentials.json not found.")
                print("Please download 'credentials.json' from Google Cloud Console (OAuth Client ID - Desktop App) ")
                print("and place it in the 'daily-economic-news-app' directory.")
                return None
            flow = InstalledAppFlow.for_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    try:
        service = build("gmail", "v1", credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def create_message(sender: str, to: str, subject: str, message_text: str) -> dict:
    """Create a message for an email.

    Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: Subject of the email.
        message_text: Content of the email.

    Returns:
        An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text, "html") # Use html for rich content
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject
    return {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, user_id: str, message: dict) -> Optional[dict]:
    """Send an email message.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

    Returns:
        Sent Message.
    """
    try:
        message = (
            service.users()
            .messages()
            .send(userId=user_id, body=message)
            .execute()
        )
        print(f"Message Id: {message['id']}")
        return message
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

if __name__ == "__main__":
    # This block will guide the user through authorization and send a test email
    print("Attempting to get Gmail service and send a test email...")
    service = get_gmail_service()
    if service:
        # Replace with a valid recipient email address for testing
        test_recipient_email = os.getenv("TEST_RECIPIENT_EMAIL", "your_email@example.com") 
        if test_recipient_email == "your_email@example.com":
            print("Please set the TEST_RECIPIENT_EMAIL environment variable or replace 'your_email@example.com' with a real email address for testing.")
        else:
            test_subject = "Daily Economic News - Test Email"
            test_body = """
            <html>
            <body>
                <p>Hello from your Daily Economic News app!</p>
                <p>This is a test email sent from the configured Gmail API.</p>
                <p>If you received this, the email sending setup is working!</p>
            </body>
            </html>
            """
            message = create_message("me", test_recipient_email, test_subject, test_body)
            send_message(service, "me", message)
            print(f"Test email sent to {test_recipient_email}")
    else:
        print("Failed to get Gmail service. Email sending will not work.")
