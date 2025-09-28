# from utils.document_management import DocumentManager

# if __name__ == '__main__':

#     filepath = "docs/ХҮНИЙ ХУВИЙН МЭДЭЭЛЭЛ ХАМГААЛАХ ТУХАЙ.docx"

#     chunks = DocumentManager.split_text_into_chunks(filepath)
#     for i, chunk in enumerate(chunks):
#         print(chunk.metadata["source"])


from utils.document_management import DocumentManager

articles = DocumentManager.segment_document("docs/ХҮНИЙ ХУВИЙН МЭДЭЭЛЭЛ ХАМГААЛАХ ТУХАЙ.docx")
chunks = DocumentManager.chunk_articles(articles, 800)

for chunk in chunks:
    print(f"{chunk}\n")