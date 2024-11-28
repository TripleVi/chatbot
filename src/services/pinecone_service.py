import os

from pinecone import Pinecone
from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

pc = Pinecone(os.environ["PINECONE_API_KEY"])
embeddings = HuggingFaceInferenceAPIEmbeddings(
    api_key=os.environ["HUGGINGFACEHUB_API_TOKEN"],
    model_name=os.environ["EMBEDDINGS_MODEL"],
)

def get_vector_store(index_name: str):
    index = pc.Index(index_name)
    return PineconeVectorStore(index, embeddings)

def split_project_desc(description: str):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
    return text_splitter.split_text(description)

def gen_project_doc_ids(id: int, doc_count: int):
    return [f"{id}#chunk{num}" for num in range(1, doc_count+1)]

async def add_project(project: dict):
    vector_store = get_vector_store("graduation-showcase2")
    splits = split_project_desc(project["description"])
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
        
    await vector_store.aadd_documents(docs, ids=ids)

async def update_project(project: dict):
    await delete_project(project["id"])
    await add_project(project)

def delete_project(id: int):
    index = pc.Index("graduation-showcase2")
    prefix = f"{id}#chunk"
    deleted = []
    for ids in index.list(prefix=prefix):
        index.delete(ids=ids)
        deleted.extend(ids)
    return deleted

def gen_proper_noun_id(id: int, source: str):
    return f"{source}#{id}"

async def add_proper_noun(id: int, text: str, source: str):
    vector_store = get_vector_store("proper-noun")
    doc = Document(text, metadata={"source": source})
    doc_id = gen_proper_noun_id(id, source)
    await vector_store.aadd_documents([doc], ids=[doc_id])

async def update_proper_noun(id: int, text: str, source: str):
    await delete_proper_noun(id, source)
    await add_proper_noun(id, text, source)

async def delete_proper_noun(id: int, source: str):
    vector_store = get_vector_store("proper-noun")
    doc_id = gen_proper_noun_id(id, source)
    await vector_store.adelete([doc_id])
