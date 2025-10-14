import os
import httpx
from typing import Optional

FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
GRAPH_API_VERSION = "v20.0" 
MESSAGES_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}/me/messages"

def send_message(recipient_id: str, message_text: str) -> Optional[dict]:
    """
    Sends a simple text message to a specific user on Messenger.
    """
    if not FB_PAGE_ACCESS_TOKEN or FB_PAGE_ACCESS_TOKEN.startswith("placeholder"):
        print("INFO: FB_PAGE_ACCESS_TOKEN not set, skipping actual message send.")
        return None

    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text},
        "messaging_type": "RESPONSE"
    }
    params = {"access_token": FB_PAGE_ACCESS_TOKEN}
    
    print(f"Sending message to user {recipient_id}: '{message_text[:100]}...'")
    try:
        with httpx.Client() as client:
            response = client.post(MESSAGES_URL, json=payload, params=params)
            response.raise_for_status()
            print("Message sent successfully to Messenger.")
            return response.json()
    except httpx.HTTPStatusError as e:
        print(f"Error sending message: {e.response.status_code}")
        print(e.response.json())
        return None

def send_message_with_button(recipient_id: str, message_text: str, button_title: str, button_url: str) -> Optional[dict]:
    """
    Sends a text message that includes a call-to-action button.
    """
    if not FB_PAGE_ACCESS_TOKEN or FB_PAGE_ACCESS_TOKEN.startswith("placeholder"):
        print("INFO: FB_PAGE_ACCESS_TOKEN not set, skipping actual message send.")
        return None

    # This check ensures the message text does not exceed Facebook's 640 character limit.
    if len(message_text) > 640:
        message_text = message_text[:637] + "..."

    payload = {
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": message_text,
                    "buttons": [
                        {
                            "type": "web_url",
                            "url": button_url,
                            "title": button_title
                        }
                    ]
                }
            }
        }
    }
    
    params = {"access_token": FB_PAGE_ACCESS_TOKEN}
    
    print(f"Sending button message to user {recipient_id}...")
    try:
        with httpx.Client() as client:
            response = client.post(MESSAGES_URL, json=payload, params=params)
            response.raise_for_status()
            print("Button message sent successfully to Messenger.")
            return response.json()
    except httpx.HTTPStatusError as e:
        print(f"Error sending button message: {e.response.status_code}")
        print(e.response.json())
        return None