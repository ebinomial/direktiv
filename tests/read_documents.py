from utils.database_management import DatabaseManager
from utils.document_management import DocumentManager

if __name__ == '__main__':

    dbms = DatabaseManager()

    query = "Гадаадын этгээдэд мэдээллийг дамжуулах тухай яах вэ?"
    response = dbms.read(query)

    print(response)

    dbms.client.close()