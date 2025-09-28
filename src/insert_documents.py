from src.database_management import DatabaseManager
from utils.document_management import DocumentManager

import os
from dotenv import load_dotenv
load_dotenv()

if __name__ == '__main__':

    filepath = "docs/ХҮНИЙ ХУВИЙН МЭДЭЭЛЭЛ ХАМГААЛАХ ТУХАЙ.docx"

    articles = DocumentManager.segment_document(filepath)
    chunks = DocumentManager.chunk_articles(articles, 800)
    
    dbms = DatabaseManager(os.getenv("EMBEDDING_SERVER"))

    ids = dbms.insert(chunks)
    print(f"Inserted documents: {ids}")

    dbms.client.close()