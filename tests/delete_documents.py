# from utils.document_management import DocumentManager

# if __name__ == '__main__':

#     filepath = "docs/ХҮНИЙ ХУВИЙН МЭДЭЭЛЭЛ ХАМГААЛАХ ТУХАЙ.docx"

#     chunks = DocumentManager.split_text_into_chunks(filepath)
#     for i, chunk in enumerate(chunks):
#         print(chunk.metadata["source"])


from src.database_management import DatabaseManager

import os
import requests
from dotenv import load_dotenv

_ = load_dotenv()

dbms = DatabaseManager(os.getenv("EMBEDDING_SERVER"))
result = dbms.delete("docs/ХҮНИЙ ХУВИЙН МЭДЭЭЛЭЛ ХАМГААЛАХ ТУХАЙ.docx")
print(result)
dbms.client.close()