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

import requests
import logging
import weaviate

from typing import List, Dict, Any

from langchain_core.documents import Document
from weaviate.classes.config import Property, DataType
from weaviate.classes.query import MetadataQuery, Filter
from weaviate.exceptions import WeaviateQueryError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class DatabaseManager:

    def __init__(self, embedding_host: str) -> None:
        self.collection_name = "Direktiv"

        self.client = weaviate.connect_to_local()
        self.collection = self.client.collections.get(self.collection_name)

        logger.info(f"Database connection established: {self.collection_name}")
        
        self.embedding_url = f"http://{embedding_host}/embed"
        
        test_response = self.encode(["test"])
        if test_response[0]:
            logger.info(f"Sentence Embedding model is available for use.")
            logger.info(f"Embed dimensions: {len(test_response[0])}")

        if not self.collection.exists():
            logger.info(f"Collection doesn't exist. Creating a new one...")
            self.collection = self.client.collections.create(
                name=self.collection_name,
                properties=[
                    Property(name="title", data_type=DataType.TEXT),
                    Property(name="body", data_type=DataType.TEXT)
                ]
            )

    def encode(self, sentences: List[str]) -> List[List[int]]:
        headers = {"Content-Type": "application/json"}
        payload = {"inputs": sentences}

        response = requests.post(
            self.embedding_url,
            headers=headers,
            json=payload
        )

        return response.json()

    def insert(self, chunks: List[Document]) -> List[str]:

        print(f"Chunks received for insertion={len(chunks)}")

        vectors = []
        for chunk in chunks:
            vector_chunk = self.encode([chunk.page_content])[0]
            vectors.append(vector_chunk)

        print(f"LEN VECTORS RETURNED: {len(vectors)}")

        uuids = []

        try:
            with self.collection.batch.fixed_size(batch_size=50) as batch:
                for i, chunk in enumerate(chunks):
                    uuid = batch.add_object(
                        properties={ "title": chunk.metadata["source"], "body": chunk.page_content },
                        vector=vectors[i]
                    )
                    uuids.append(str(uuid))
                    if batch.number_errors > 10:
                        print("Batch import stopped due to excessive errors.")
                        break

            failed_objects = self.collection.batch.failed_objects
            if failed_objects:
                print(f"Number of failed imports: {len(failed_objects)}")
                print(f"First failed object: {failed_objects[0]}")

        except Exception as err:
            print(f"Exception occured in insertion:\n{str(err)}")
            return []

        return uuids
    
    def read(self, query: str, limit: int = 2) -> List[Dict[str, Any]]:
        
        query_vector = self.encode([query])[0]
        
        response = self.collection.query.near_vector(
            near_vector=query_vector,
            limit=limit,
            return_metadata=MetadataQuery(distance=True)
        )

        objects = []

        for obj in response.objects:
            objects.append({
                "distance": obj.metadata.distance,
                "title": obj.properties["title"],
                "body": obj.properties["body"]
            })

        return objects
    
    def delete(self, title: str = None) -> Dict[str, int]:
        try:
            deleted = self.collection.data.delete_many(
                where=Filter.by_property("title").like(title)
            )
            return {
                "failed": deleted.failed,
                "successful": deleted.successful,
                "matched": deleted.matches
            }
        
        except Exception as err:
            print(f"There appeared error deleting objects: {str(err)}")
            return { }
        
    def count(self) -> int:
        try:
            count = self.collection.aggregate.over_all(total_count=True)
            return count.total_count
        except WeaviateQueryError as e:
            print(f"Counting error: {str(e)}")