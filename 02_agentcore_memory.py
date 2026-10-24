import csv
import json
import os
from typing import List

import boto3
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_aws import BedrockEmbeddings
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain.agents import create_agent

from dotenv import load_dotenv
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from langgraph_checkpoint_aws import AgentCoreMemorySaver, AgentCoreMemoryStore

app = BedrockAgentCoreApp()
_ = load_dotenv()

REGION = "us-east-1"
MEMORY_ID = "agent_FAQ_memory-1miyurA534"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

#Initialize Memory componets
# Checkpointer is short memory
checkpointer = AgentCoreMemorySaver(memory_id=MEMORY_ID)
# Store is a much longer memery that the agent can use to remember your personality
store = AgentCoreMemoryStore(memory_id=MEMORY_ID)


def get_secret(secret_name: str, region_name: str = "us-east-1") -> str:
    """Retrieve secret from AWS Secrets Manager"""
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(get_secret_value_response['SecretString'])
        return secret.get('GROQ_API_KEY')
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        raise


# Retrieve GROQ API key from Secrets Manager (or fallback to env for local development)
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or get_secret("bedrock-agentcore/groq-api-key", REGION)


def load_faq_csv(path: str) -> List[Document]:
    docs = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            q = row["question"].strip()
            a = row["answer"].strip()
            docs.append(Document(page_content=f"Q: {q}\nA: {a}"))
    return docs


emb = BedrockEmbeddings(
    model_id="amazon.titan-embed-text-v2:0",
    region_name=os.getenv("AWS_REGION", "us-east-1"),
)

# Use pre-built FAISS index (created by build_faiss_index.py)
FAISS_INDEX_PATH = "./faiss_index"
faq_store = FAISS.load_local(FAISS_INDEX_PATH, emb, allow_dangerous_deserialization=True)


@tool
def search_faq(query: str) -> str:
    """Search the FAQ knowledge base for relevant information.
    Use this when the user asks questions about products, services, or policies.

    Args:
        query: The search query to find relevant FAQ entries.

    Returns:
        Relevant FAQ entries that might answer the question.
    """
    print(f"[TOOL] search_faq called with: {query}")

    results = faq_store.similarity_search(query, k=3)

    print(f"[TOOL] Found {len(results)} results")
    results = faq_store.similarity_search(query, k=3)
    for i, doc in enumerate(results):
        print(f"[RESULT {i+1}]")
        print(doc.page_content)

    if not results:
        return "No relevant FAQ entries found."
    context = "\n\n---\n\n".join([
        f"FAQ Entry {i+1}:\n{doc.page_content}"
        for i, doc in enumerate(results)
    ])
    return f"Found {len(results)} relevant FAQ entries:\n\n{context}"


@tool
def search_detailed_faq(query: str, num_results: int = 5) -> str:
    """Search the FAQ knowledge base with more results for complex queries.
    Use when the initial search does not provide enough information.

    Args:
        query: The search query string.
        num_results: Number of results to retrieve (default: 5).

    Returns:
        More comprehensive FAQ entries.
    """
    results = faq_store.similarity_search(query, k=num_results)
    if not results:
        return "No relevant FAQ entries found."
    context = "\n\n---\n\n".join([
        f"FAQ Entry {i+1}:\n{doc.page_content}"
        for i, doc in enumerate(results)
    ])
    return f"Found {len(results)} detailed FAQ entries:\n\n{context}"


@tool
def reformulate_query(original_query: str, focus_aspect: str) -> str:
    """Reformulate the query to focus on a specific aspect like pricing, activation, or troubleshooting.

    Args:
        original_query: The original user question.
        focus_aspect: The specific aspect to focus on (e.g. 'pricing', 'activation', 'troubleshooting').

    Returns:
        Results for the reformulated query focused on the specified aspect.
    """
    reformulated = f"{focus_aspect} related to {original_query}"
    results = faq_store.similarity_search(reformulated, k=3)
    if not results:
        return f"No results found for aspect: {focus_aspect}"
    context = "\n\n---\n\n".join([
        f"Entry {i+1}:\n{doc.page_content}"
        for i, doc in enumerate(results)
    ])
    return f"Results for '{focus_aspect}' aspect:\n\n{context}"


tools = [search_faq, search_detailed_faq, reformulate_query]

model = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    api_key=GROQ_API_KEY
)

system_prompt = """
You are an AI Support Agent, a professional customer support assistant.

Your responsibility is to provide accurate, helpful, and customer-friendly answers using the company knowledge base.

PRIMARY OBJECTIVE
- Resolve the customer's question as clearly as possible.
- Use the knowledge base as the source of truth.
- Give direct answers before providing additional details.
- Maintain a professional, helpful, and empathetic tone.

RETRIEVAL STRATEGY

1. ALWAYS search the knowledge base before answering.
2. Start with search_faq.
3. If the results are incomplete, ambiguous, or insufficient:
   - Use search_detailed_faq.
4. If the question can be interpreted in multiple ways:
   - Use reformulate_query and search again.
5. Gather information from multiple results when necessary.
6. Never invent policies, prices, procedures, or technical details.
7. If information cannot be found, explicitly state that the knowledge base does not contain enough information.

ANSWERING RULES

- Answer the user's actual question first.
- Then provide supporting details.
- Keep answers concise but complete.
- Use bullet points for steps, requirements, benefits, or troubleshooting.
- Avoid unnecessary repetition.
- Do not expose internal tool usage.
- Do not mention retrieval processes or search operations.

CUSTOMER SUPPORT BEHAVIOR

For troubleshooting:
- Explain the likely cause.
- Provide step-by-step actions.
- Mention escalation options if available.

For account-related issues:
- Explain verification requirements.
- Explain available actions.
- Mention security considerations when relevant.

For billing questions:
- Explain possible causes.
- Mention invoice and payment options if available.
- Guide the customer toward resolution.

For SIM, eSIM, roaming, or connectivity issues:
- Provide practical steps in order.
- Include prerequisites and limitations when known.

RESPONSE FORMAT

Use this structure whenever appropriate:

Direct Answer

- Main answer to the question.

Details

- Relevant supporting information.

Next Steps

- Recommended actions for the customer.

UNCERTAINTY HANDLING

If confidence is low:
- Say what information was found.
- Explain what is missing.
- Avoid speculation.

Example:

User: "How do I activate an eSIM?"

Good Response:
- Open the Lauki app and navigate to eSIM Activation.
- Complete identity verification.
- Request the eSIM profile.
- Scan the generated QR code using your device.
- Confirm installation.

Important:
- The physical SIM is automatically deactivated after successful eSIM activation.
- Ensure your device supports eSIM before starting.

If no relevant information exists in the knowledge base:
"I couldn't find enough information in the knowledge base to answer that accurately."""

print("Creating agent with memory support...")
agent = create_agent(
    model=model,
    tools=tools,
    checkpointer=checkpointer,
    system_prompt=system_prompt
)
print("Agent created successfully with memory support")


@app.entrypoint
def agent_invocation(payload, context):
    print("Received Payload", payload)
    print("Received context", context)

    query = payload.get("prompt", "No prompt found in input")

    # Get session/thread ID from context (attribute) or payload (dict), or use a default
    thread_id = context.session_id if hasattr(context, 'session_id') and context.session_id else payload.get("session_id", "default-session")

    print(f"Using thread_id: {thread_id}")

    # Configure the agent with thread_id and actor_id for memory persistence
    config = {"configurable": {"thread_id": thread_id, "actor_id": "default"}}

    # Invoke agent with memory support
    result = agent.invoke(
        {"messages": [("human", query)]},
        config=config
    )

    print("Result", result)
    return {"response": result["messages"][-1].content}


if __name__ == "__main__":
    app.run()