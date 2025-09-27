import os
import requests
from dotenv import load_dotenv

_ = load_dotenv()

if __name__ == '__main__':

    EMBEDDING_SERVER = os.getenv("EMBEDDING_SERVER")
    API_URL = f"http://{EMBEDDING_SERVER}/embed"

    headers = {"Content-Type": "application/json"}
    payload = {"inputs": "What makes you a better person?"}

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload
    )

    embed_vectors = response.json()[0]
    print(embed_vectors)
    print(len(embed_vectors))
    print(type(embed_vectors))