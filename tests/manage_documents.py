from utils.document_management import DocumentManager

import os
from dotenv import load_dotenv
from src.database_management import DatabaseManager

load_dotenv()

if __name__ == '__main__':

    dbms = DatabaseManager(os.getenv("EMBEDDING_SERVER"))

    user_query = """
    Хувийн мэдээллийн зөрчил гарсан гомдлыг хаана гаргах талаар
    """
    response = dbms.read(user_query)
    print(response)

    dbms.client.close()