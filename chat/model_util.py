import os
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from dotenv import load_dotenv
load_dotenv()

def get_llm():
    # Get API key from environment variable
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    # Initialize ChatOpenAI with streaming capability
    llm = ChatOpenAI(
        openai_api_key=openai_api_key,
        model_name="gpt-4o-mini",
        temperature=0.1,
        streaming=True,
        callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
    )

    return llm


def get_qa_chain(vectorstore):
    # Get LLM
    llm = get_llm()

    # Create a retriever from vectorstore
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )

    # Create ConversationalRetrievalChain
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=False,
        verbose=True
    )

    return qa_chain
