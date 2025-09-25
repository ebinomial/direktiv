from utils.document_management import DocumentManager

if __name__ == '__main__':

    filepath = "docs/ХҮНИЙ ХУВИЙН МЭДЭЭЛЭЛ ХАМГААЛАХ ТУХАЙ.docx"

    chunks = DocumentManager.split_text_into_chunks(filepath)
    for i, chunk in enumerate(chunks):
        print(chunk.metadata["source"])