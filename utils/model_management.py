# MIT License

# Copyright (c) 2025 Erdenebileg Byambadorj

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import asyncio
import logging

from typing import List, Dict, Any

from openai import AsyncOpenAI
from dotenv import load_dotenv

_ = load_dotenv()

ModelClient = AsyncOpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# ynz buriin clienteesee hamaaraad ModelClient-ee updatelenee
def setup_client(api_key: str) -> ModelClient | None:
    """
    Sets up and authenticates to a client to use for further token generation.
    Args:
        base_url (str): Local or remote server hosting the model.
        api_key (str): Optional key for authentication into the model.
    Returns:
        ModelClient: a custom type applicable to different clients (OpenAI, Gemini etc).
    """

    try:
        
        # TODO: check the type of client to spawn
        client = AsyncOpenAI(api_key=api_key)

        logger.info(f"Client amjilttai uussen shu!")
        return client

    except Exception as err:
        logger.info(f"Client uusgehed aldaa garaw: {str(err)}")
        return None

# Enenees gaduur yur ni ymr neg generation horiotoi kk.
async def generate_message(client: ModelClient, model: str, 
                           context: List[Dict[str, str]]) -> str:
    """
    Generates a query in the context of the interaction history from the stated model.
    Args:
        client (ModelClient): driver to the model host
        model (str): name of the model for use running on the host
        context (List[Dict[str, str]]): list of interactive roles and corresponding content text messages
    
    Returns:
        str: Model response either the final output or a tool call.
    """

    stream = await client.chat.completions.create(
        messages=context, 
        model=model, 
        stream=True
    )

    full_response = str()
    
    print(f"\033[32m>>>АГЕНТ: ", end="")
    async for token in stream:
        if token.choices[0].delta.content:
            print(token.choices[0].delta.content, end="")
            full_response += token.choices[0].delta.content

    print("\033[0m\n")
    return full_response

if __name__ == '__main__':

    base_url = os.getenv("BASE_URL", None)
    api_key = os.getenv("API_KEY", None)

    print(f">>>", end="")
    test_question = input()

    if (base_url is None) or (api_key is None):
        logger.info("Env BASE_URL and API_KEY alga.")

    else:
        # For testing purposes hehe.
        client = setup_client(base_url, api_key)
        asyncio.run(generate_message(client, 'egune', [], test_question))