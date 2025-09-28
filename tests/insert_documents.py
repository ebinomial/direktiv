from src.database_management import DatabaseManager
from utils.document_management import DocumentManager

import os
from dotenv import load_dotenv
load_dotenv()

if __name__ == '__main__':

    filepath = "docs/ХҮНИЙ ХУВИЙН МЭДЭЭЛЭЛ ХАМГААЛАХ ТУХАЙ.docx"

    chunks = DocumentManager.split_text_into_chunks(filepath)
    dbms = DatabaseManager(os.getenv("EMBEDDING_SERVER"))

    ids = dbms.insert(chunks)
    print(ids)

    dbms.client.close()