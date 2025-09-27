import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from dotenv import load_dotenv

load_dotenv()

# Initialize WebClient with your bot token
client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

def send_message_to_channel(channel_name, message):
    try:
        # Send message to specific channel
        response = client.chat_postMessage(
            channel=channel_name,
            text=message
        )
        print(f"Message sent successfully: {response['message']['text']}")
        return response
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")

# Example usage
if __name__ == "__main__":
    send_message_to_channel("#mcs-legal-questions", "Сайн уу? Би туршилтын бот байна. Намайг хүлээж авсан уу?")