from utils.database_management import DatabaseManager
from utils.document_management import DocumentManager

if __name__ == '__main__':

    filepath = "docs/ХҮНИЙ ХУВИЙН МЭДЭЭЛЭЛ ХАМГААЛАХ ТУХАЙ.docx"

    chunks = DocumentManager.split_text_into_chunks(filepath)
    dbms = DatabaseManager()

    ids = dbms.insert(chunks)
    print(ids)

    dbms.client.close()