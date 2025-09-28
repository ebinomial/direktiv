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

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from database_management import DatabaseManager

load_dotenv()

embedding_host = os.getenv("EMBEDDING_SERVER")

weaviate_mcp = FastMCP("weaviate_dbms")
dbms = DatabaseManager(embedding_host)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

@weaviate_mcp.tool()
async def search_vector_database(query: str, limit: int = 5) -> str:
    """
    Searches the Weaviate vector database collection pertaining 
    to the application for response document chunks by passing the 
    query in this tool. Pass the query in string and the function
    converts it into a vector, searches the database and identifies
    the nearest-neighboring document vectors in the collection. The
    identified document chunks are concatenated into a single string
    to be returned.
    """

    db_response = dbms.read(query, limit)

    if len(db_response) > 0:
        str_repr = ""
        for entity in db_response:
            str_repr += f"""
            Title: {entity['title']}\n
            Response chunk: {entity['body']}\n
            Relevance score: {(1-entity['distance'])*100}%\n\n
            """
            
        return str_repr

    return f"No response has been found for: `{query}`."

@weaviate_mcp.tool()
async def count_collection_vectors() -> int:
    """
    Counts the number of vectors present in the Weaviate database
    collection. No need to specify the collection as it has been 
    configured a priori.
    """
    return dbms.count()

if __name__ == '__main__':
    weaviate_mcp.run(transport="stdio")
    dbms.client.close()