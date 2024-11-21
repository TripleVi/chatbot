import os

from pinecone import Pinecone
from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

def gen_project_doc_ids(id: int, doc_count: int):
    return [f"{id}#chunk{num}" for num in range(1, doc_count+1)]

def add_project(project: dict):
    pc = Pinecone(os.environ["PINECONE_API_KEY"])
    index = pc.Index("graduation-showcase2")
    embeddings = HuggingFaceBgeEmbeddings(model_name=os.environ["EMBEDDINGS_MODEL"])
    vector_store = PineconeVectorStore(index, embeddings)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
    splits = text_splitter.split_text(project["description"])
    ids = gen_project_doc_ids(project["id"], len(splits))
    text_authors = [
        f"* {author["name"]} - Email: {author["email"]}"
        for author in project["authors"]
    ]
    text_author = "\n".join(text_authors)
    docs = []
    content = f"""ID: {project["id"]}

Year: {project["year"]}

Authors:
{text_author}

Title: {project["title"]}

Content: {splits[0]}"""
    docs.append(Document(
        page_content=content,
        metadata={"project_id": project["id"]},
    ))

    for split in splits[1:]:
        content = f"""ID: {project["id"]}

Title: {project["title"]}

Content: {split}"""
        docs.append(Document(
            page_content=content,
            metadata={"project_id": project["id"]},
        ))
        
    vector_store.add_documents(docs, ids=ids)

def update_project(project: dict):
    pc = Pinecone(os.environ["PINECONE_API_KEY"])
    index = pc.Index("graduation-showcase2")
    embeddings = HuggingFaceBgeEmbeddings(model_name=os.environ["EMBEDDINGS_MODEL"])
    vector_store = PineconeVectorStore(index, embeddings)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)

    splits = text_splitter.split_text(project["description"])
    ids = gen_project_doc_ids(project["id"], len(splits))
    text_authors = [
        f"* {author["name"]} - Email: {author["email"]}"
        for author in project["authors"]
    ]
    text_author = "\n".join(text_authors)
    docs = []
    content = f"""ID: {project["id"]}

Year: {project["year"]}

Authors:
{text_author}

Title: {project["title"]}

Content: {splits[0]}"""
    docs.append(Document(
        page_content=content,
        metadata={"project_id": project["id"]},
    ))

    for split in splits[1:]:
        content = f"""ID: {project["id"]}

Title: {project["title"]}

Content: {split}"""
        docs.append(Document(
            page_content=content,
            metadata={"project_id": project["id"]},
        ))

    vector_store.add_documents(docs, ids=ids)

def delete_project(id: int):
    pc = Pinecone(os.environ["PINECONE_API_KEY"])
    index = pc.Index("graduation-showcase2")
    prefix = f"{id}#chunk"
    deleted = []
    for ids in index.list(prefix=prefix):
        index.delete(ids=ids)
        deleted.extend(ids)
    return deleted

def gen_proper_noun_id(id: int, source: str):
    return f"{source}#{id}"

def add_proper_noun(id: int, text: str, source: str):
    pc = Pinecone(os.environ["PINECONE_API_KEY"])
    index = pc.Index("proper-noun")
    embeddings = HuggingFaceBgeEmbeddings(model_name=os.environ["EMBEDDINGS_MODEL"])
    vector_store = PineconeVectorStore(index, embeddings)
    doc = Document(text, metadata={"source": source})
    doc_id = gen_proper_noun_id(id, source)
    vector_store.add_documents([doc], ids=[doc_id])

def update_proper_noun(id: int, text: str, source: str):
    pc = Pinecone(os.environ["PINECONE_API_KEY"])
    index = pc.Index("proper-noun")
    embeddings = HuggingFaceBgeEmbeddings(model_name=os.environ["EMBEDDINGS_MODEL"])
    vector_store = PineconeVectorStore(index, embeddings)
    doc = Document(text, metadata={"source": source})
    doc_id = gen_proper_noun_id(id, source)
    index.delete([doc_id])
    vector_store.add_documents([doc], ids=[doc_id])

def delete_proper_noun(id: int, source: str):
    pc = Pinecone(os.environ["PINECONE_API_KEY"])
    index = pc.Index("proper-noun")
    doc_id = gen_proper_noun_id(id, source)
    index.delete([doc_id])
