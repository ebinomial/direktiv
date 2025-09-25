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

import re
from typing import List

from langchain_core.documents import Document
from langchain_community.document_loaders import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentManager:

    @classmethod
    def split_text_into_chunks(cls, filepath: str, is_legal_document: bool = True) -> List[Document]:
        """
        Currently this is the main input streamline as legalinfo.mn allows
        us to download regulations in docx format.

        Splits each document into text chunks according to the separators
        as well as chunk size, with certain overlaps between subsequent chunks.
        Args:
            filepath (str): Docx path to read the document from
            is_legal_document (bool): If the loading document is related to legality
        
        Returns:
            List[Document]: List of documents split into segments as per the requirements
        """

        loader = Docx2txtLoader(filepath)
        documents = loader.load()

        # dediin ded zuil angiudiin butssees harwal tab arilgaad 
        # daraa ni newline arilgah heregtei
        clean_document = re.sub(r"\t{1,}", '', documents[0].page_content)
        clean_document = re.sub(r"\n{3,}", '\n', clean_document)

        documents[0].page_content = clean_document


        # dugaar zuil angiar ni hamt huwaahiig zorihgui bol yunii tuhai
        # specific article yriad bgaagaa model olj medehgui.
        if is_legal_document:
            separators = [
                r"\d{1,} дүгээр зүйл",
                r"\d{1,} дугаар зүйл"
            ]
        else:
            separators = []

        separators += ["\n\n", "\n", ". "]
        
        text_splitter = RecursiveCharacterTextSplitter(
            separators=separators,
            chunk_size=1200,
            chunk_overlap=250,
            length_function=len,
            is_separator_regex=True
        )

        chunks = text_splitter.split_documents(documents)

        return chunks