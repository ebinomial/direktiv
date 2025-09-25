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

import weaviate

from typing import List, Dict, Any

from numpy import ndarray
from FlagEmbedding import BGEM3FlagModel
from langchain_core.documents import Document
from weaviate.classes.config import Property, DataType
from weaviate.classes.query import MetadataQuery

class DatabaseManager:

    def __init__(self, local_model: bool = True):
        self.collection_name = "Direktiv"

        self.client = weaviate.connect_to_local()
        self.collection = self.client.collections.get(self.collection_name)

        self.model = BGEM3FlagModel("BAAI/BGE-m3", use_fp16=True, devices="cuda")

        if not self.collection.exists():
            print(f"Collection doesn't exist. Creating a new one...")
            self.collection = self.client.collections.create(
                name=self.collection_name,
                properties=[
                    Property(name="title", data_type=DataType.TEXT),
                    Property(name="body", data_type=DataType.TEXT)
                ]
            )

    def encode(self, sentences: List[str]) -> List[ndarray]:
        vectors = self.model.encode(sentences)["dense_vecs"]
        return vectors

    def insert(self, chunks: List[Document]) -> List[str]:

        sentences = [chunk.page_content for chunk in chunks]
        vectors = self.encode(sentences)

        uuids = []

        with self.collection.batch.fixed_size(batch_size=50) as batch:
            for i, chunk in enumerate(chunks):
                uuid = batch.add_object(
                    properties={ "title": chunk.metadata["source"], "body": chunk.page_content },
                    vector=vectors[i].tolist()
                )
                uuids.append(str(uuid))
                if batch.number_errors > 10:
                    print("Batch import stopped due to excessive errors.")
                    break

        failed_objects = self.collection.batch.failed_objects
        if failed_objects:
            print(f"Number of failed imports: {len(failed_objects)}")
            print(f"First failed object: {failed_objects[0]}")

        return uuids
    
    def read(self, query: str, limit: int = 2) -> List[Dict[str, Any]]:
        
        query_vector = self.encode([query])[0]
        
        response = self.collection.query.near_vector(
            near_vector=query_vector.tolist(),
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


if __name__ == '__main__':
    manager = DatabaseManager()
    manager.client.close()
