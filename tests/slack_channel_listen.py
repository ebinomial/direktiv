import os

from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest

load_dotenv()

app_token = os.getenv("SLACK_APP_TOKEN")
bot_token = os.getenv("SLACK_BOT_TOKEN")

# Initialize SocketModeClient with app-level token + WebClient
client = SocketModeClient(
    app_token=app_token,
    web_client=WebClient(token=bot_token)
)

def process_events(client: SocketModeClient, req: SocketModeRequest):
    """Process incoming Slack events"""

    response = SocketModeResponse(envelope_id=req.envelope_id)
    client.send_socket_mode_response(response)
    

    if req.type == "events_api":
        event = req.payload["event"]
        
        if event["type"] == "message" and event.get("subtype") is None:
            channel_id = event["channel"]
            user_id = event["user"]
            message_text = event.get("text", "")
            
            if user_id == client.web_client.auth_test()["user_id"]:
                return
            
            print(f"Received message: '{message_text}' in channel: {channel_id}")
            
            send_response(client, channel_id, f"Сайн уу! <@{user_id}>")

def send_response(client: SocketModeClient, channel_id: str, message: str):
    """Send a response message to a channel"""
    try:
        response = client.web_client.chat_postMessage(
            channel=channel_id,
            text=message
        )
        print(f"Response sent: {message}")
    except Exception as e:
        print(f"Error sending response: {e}")

def send_message_to_specific_channel(client: SocketModeClient, channel_name: str, message: str):
    """Send a message to a specific channel by name"""
    try:
        response = client.web_client.chat_postMessage(
            channel=channel_name,
            text=message
        )
        print(f"Message sent to {channel_name}: {message}")
        return response
    except Exception as e:
        print(f"Error sending message to {channel_name}: {e}")


client.socket_mode_request_listeners.append(process_events)

if __name__ == "__main__":

    send_message_to_specific_channel(client, "#mcs-legal-questions", "🤖 Сайн уу? Би сонсож байгаа шүү...")
    
    client.connect()
    
    try:
        # Keep the bot running
        from time import sleep
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print("Bot is shutting down...")
        client.disconnect()