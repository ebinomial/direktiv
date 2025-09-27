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
import logging
import asyncio

from dotenv import load_dotenv
from src.mcp_client import StdioClient

_ = load_dotenv()

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

async def main():

    model_name = os.getenv("MODEL_NAME")
    api_key = os.getenv("OPENAI_API_KEY")

    print(f"{model_name}\n{api_key}")
    # Create the client to interact with the MCP servers
    mcp_client = StdioClient(model_name, api_key)

    # Configure the server parameters
    server_configs = {
        "weaviate_vector_database": {
            "command": "python",
            "transport": "stdio",
            "args": [
                "src/weaviate_server.py"
            ]
        }
    }

    try:
        # Set up MCP servers
        _ = await mcp_client.connect_to_servers(server_configs)

        # Get in indefinite loop of QA.
        _ = await mcp_client.initiate_cycle()

    except Exception as e:
        logger.error(f"Error took place in the agent using MCP client.\n{str(e)}")

if __name__ == '__main__':
    asyncio.run(main())