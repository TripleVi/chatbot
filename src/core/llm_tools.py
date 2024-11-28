import os

from langchain_google_vertexai import ChatVertexAI
from langchain.tools.retriever import create_retriever_tool
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.tools import tool

from src.services import pinecone_service

def init_sql_db():
    database_uri = f"mysql+mysqlconnector://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_SCHEMA"]}"
    return SQLDatabase.from_uri(
        database_uri,
        include_tables=['major', 'topic', 'project_summary'],
        view_support=True,
    )

@tool(parse_docstring=True)
def sql_db_list_tables():
    """Output is a dict containing a comma-separated list of tables in the database along with their descriptions.
    """
    db = init_sql_db()
    tables = db.get_usable_table_names()
    return {
        "tables": ", ".join(tables),
        "description": "The relationship between Major and Topic is one-to-many. The relationship between Topic and Project is one-to-many. Each Major represents an academic discipline of the university. Each Topic belongs to a specific discipline and represents a project category. Each Project_Summary belongs to a specific topic and represents summary information about a project.",
    }

def get_sql_tools():
    model = ChatVertexAI(model="gemini-1.5-flash-002", temperature=0, max_tokens=300)
    db = init_sql_db()
    toolkit = SQLDatabaseToolkit(db=db, llm=model)
    tools = toolkit.get_tools()
    for i, t in enumerate(tools):
        if t.name == "sql_db_list_tables":
            del tools[i]
            break
    tools.append(sql_db_list_tables)
    return tools

@tool(parse_docstring=True)
async def retrieve_proper_nouns(query: str, source: str) -> str:
    """Search and return values most similar to the proper noun within a specific table.

    Args:
        query: An approximate spelling of the proper noun to look up in retriever.
        source: A table name to which the proper noun belongs.
    """
    vector_store = pinecone_service.get_vector_store("proper-noun")
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": 5,
            "score_threshold": 0.75,
            "filter": {"source": source},
        },
    )
    docs = await retriever.ainvoke(query)
    return "\n\n".join(doc.page_content for doc in docs)

def projects_retriever_tool():
    vector_store = pinecone_service.get_vector_store("graduation-showcase2")
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 20, "score_threshold": 0.7},
    )
    return create_retriever_tool(
        retriever,
        "retrieve_graduation_projects",
        "Search and return excerpts from Vietnamese articles about University of Greenwich students' graduation projects.",
    )

def get_tools():
    return [
        *get_sql_tools(),
        projects_retriever_tool(),
        retrieve_proper_nouns,
    ]
