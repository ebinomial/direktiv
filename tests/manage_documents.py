from src.database_management import DatabaseManager
from utils.document_management import DocumentManager

count = True
read = False
delete = False

import os
from dotenv import load_dotenv
load_dotenv()

if __name__ == '__main__':

    dbms = DatabaseManager(os.getenv("EMBEDDING_SERVER"))

    if count:
        cnt = dbms.count()
        print(f"count: {cnt}")

    if read:
        query = "Гадаадын этгээдэд мэдээллийг дамжуулах тухай яах вэ?"
        response = dbms.read(query)

    if delete:
        response = dbms.delete("docs/ХҮНИЙ ХУВИЙН МЭДЭЭЛЭЛ ХАМГААЛАХ ТУХАЙ.docx")

    dbms.client.close()