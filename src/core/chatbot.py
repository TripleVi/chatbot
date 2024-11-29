import os

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_vertexai import ChatVertexAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from src.repositories import chat_repo
from .llm_tools import get_tools

def get_system_message():
    return (
"""The system is used to manage and showcase Greenwich University students' graduation projects. You are a friendly assistant tasked with answering questions about these projects in Vietnamese. Use only the provided context in combination with user information to answer, keeping responses concise and, if possible, in bullet points. If the information isn't available in the context, just say that you don't know. Avoid generating answers without relevant context.

There are two options for retrieving project information:
1. Use the retriever tool to obtain detailed project descriptions without statistics.
2. Use the SQL database to gather project statistics without detailed descriptions.

SQL Database Usage Guidelines:

a. To interact with the database, create a syntactically correct MySQL query based on user input. To create a correct query, you MUST follow this sequence of SQL tool invocations, making only one tool call per response and moving to the next step only if the previous one succeeds:
1. See what tables are available in the database.
2. Query the schema of the tables most relevant to the question.
3. Execute the query. If filter on a proper noun, ALWAYS look up the filter value using the retriever tool before executing. If there's an error while executing a query, revise it and try again.

b. When crafting queries, you MUST follow these rules:
* ALWAYS limit the number of results to at most 5 unless the user specifies a different amount, but NEVER exceed 20.
* Can order the results to return the most informative data.
* NEVER query all columns in a table and non-existent columns. Only select the relevant columns needed to answer the question.
* NEVER use the LIKE operator in a WHERE clause.
* NEVER make any DML statements (INSERT, UPDATE, DELETE, DROP, etc.).""")

async def gen_chat_title(input: str):
    prompt_template = ChatPromptTemplate([
        ("system", "You are a friendly assistant. Provide a concise Vietnamese title to the conversation based on the following question. Please respond only with the title in affirmative form, without any special characters (e.g., '.', '?') at the end."),
        ("human", "{text}")
    ])
    model = ChatVertexAI(model=os.environ["GOOGLE_MODEL2"], temperature=1, max_tokens=40)
    chain = prompt_template | model | StrOutputParser()
    response = await chain.ainvoke({"text": input})
    return response.strip()

def get_llm_messages(raw_messages: list[dict]):
    return [
        HumanMessage(m["content"]) if i % 2 == 0 else AIMessage(m["content"])
        for i, m in enumerate(raw_messages)
    ]

async def process(input: str, chat_id: int | None = None):
    system_message = get_system_message()
    chat_history = [HumanMessage(input)]
    if chat_id:
        summary, raw_messages = await chat_repo.get_chat_history(chat_id)
        chat_history = get_llm_messages(raw_messages) + chat_history
        if summary:
            summary_message = f"\n\nSummary of the conversation earlier: {summary}"
            system_message += summary_message
    prompt_template = ChatPromptTemplate([
        ("system", system_message),
        ("placeholder", "{chat_history}")
    ])
    model = ChatVertexAI(model=os.environ["GOOGLE_MODEL"], temperature=1)
    tools = get_tools()
    available_tools = {}
    for tool in tools:
        available_tools[tool.name] = tool
    model_with_tools = model.bind_tools(tools)
    chain = (
        {"chat_history": RunnablePassthrough()}
        | prompt_template
        | model_with_tools
    )
    chunks = chain.astream(chat_history)
    message_chunk = await anext(chunks)
    while message_chunk.tool_calls:
        async for chunk in chunks:
            message_chunk += chunk
        chat_history.append(message_chunk)
        for tool_call in message_chunk.tool_calls:
            selected_tool = available_tools[tool_call["name"].lower()]
            tool_message = await selected_tool.ainvoke(tool_call)
            chat_history.append(tool_message)
        chunks = chain.astream(chat_history)
        message_chunk = await anext(chunks)
    async def content_generator():
        yield message_chunk.content
        async for chunk in chunks:
            yield chunk.content
    return content_generator()

async def summarize_conversation(id: int):
    summary, raw_messages = await chat_repo.get_chat_history(id)
    chat_history = get_llm_messages(raw_messages[:-2])
    if not chat_history:
        return
    model = ChatVertexAI(model=os.environ["GOOGLE_MODEL2"], temperature=1, max_tokens=500)
    tokens = model.get_num_tokens_from_messages(chat_history)
    if tokens <= 300 and len(chat_history) <= 8:
        return
    summary_id = chat_history[-1]["id"]
    if summary:
        summary_message = f"Here is a summary of the conversation so far: {summary}\n\nExtend the summary by taking into account the new messages above, using the original language, retaining only the key points and user information, excluding greetings, thanks, goodbyes and pleasantries, and eliminating duplicate conversations. The paragraph should be brief and concise."
    else:
        summary_message = "Briefly and concisely summarize the above conversation in one paragraph, using the original language, retaining only the key points and user information, excluding greetings, thanks, goodbyes and pleasantries, and eliminating duplicate conversations."
    chat_history.append(HumanMessage(content=summary_message))
    chain = model | StrOutputParser()
    response = await chain.ainvoke(chat_history)
    await chat_repo.update_summary(id, response, summary_id)
