# Enterprise-Scale Agentic AI with AWS Bedrock AgentCore: Production Deployment Framework

<div align="center">

![Architecture](docs/images/architecture_diagram.svg)

**A production-ready prototype for deploying intelligent AI agents at enterprise scale using AWS Bedrock AgentCore**

*Solving the challenges of deploying Agentic AI systems in enterprise environments with scalability, reliability, and cost-effectiveness*

[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-orange?logo=amazon-aws)](https://aws.amazon.com/bedrock/)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-Framework-green)](https://www.langchain.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## Table of Contents

- [Overview](#overview)
- [The Enterprise Challenge](#the-enterprise-challenge)
- [Why AWS Bedrock AgentCore?](#why-aws-bedrock-agentcore)
- [Project Architecture](#project-architecture)
- [Key Features](#key-features)
- [Prerequisites](#prerequisites)
- [Step-by-Step Deployment Guide](#step-by-step-deployment-guide)
  - [1. Environment Setup](#1-environment-setup)
  - [2. AWS Configuration](#2-aws-configuration)
  - [3. API Keys Setup](#3-api-keys-setup)
  - [4. Agent Configuration](#4-agent-configuration)
  - [5. Deployment to AWS](#5-deployment-to-aws)
  - [6. Memory Configuration](#6-memory-configuration)
- [Code Architecture Deep Dive](#code-architecture-deep-dive)
- [Vector Database Strategy](#vector-database-strategy)
- [Frontend Integration](#frontend-integration)
- [Production Considerations](#production-considerations)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This project demonstrates a **production-ready architecture** for deploying intelligent, memory-enabled AI agents at enterprise scale using **AWS Bedrock AgentCore**. It showcases how organizations can overcome the complexities of agentic AI deployment while maintaining scalability, reliability, and cost-effectiveness.

### What You Will Build

- **Intelligent FAQ Agent** with semantic search capabilities powered by FAISS vector store
- **Memory-Enabled Conversations** using AWS AgentCore Memory Store for personalized interactions
- **Enterprise-Grade Deployment** on AWS infrastructure with CloudWatch monitoring
- **Multi-Channel Frontend** with React-based chat interface
- **Scalable Vector Search** using Amazon Bedrock Titan Embeddings

---

## The Enterprise Challenge

Deploying agentic AI systems in production environments presents significant challenges that go far beyond simply calling an API. This project is a direct response to these real-world obstacles:

### 1. Infrastructure Complexity

Traditional AI deployments require extensive DevOps expertise, container orchestration (Kubernetes, ECS), and infrastructure management. Teams spend more time managing infrastructure than building intelligent features. Engineers must maintain Docker registries, load balancers, auto-scaling groups, and CI/CD pipelines just to serve a single AI model.

### 2. Scalability Limitations

Most prototype solutions fail under production load. When thousands of concurrent users hit your agent simultaneously, a single-instance Python process becomes a bottleneck. Memory management, vector search performance, and LLM throughput all degrade under scale. The gap between a demo that works for 10 users and a system that handles 10,000 users is enormous.

### 3. Memory and State Persistence

Stateless agents provide poor user experience. Every conversation starts from scratch unless you build sophisticated state management. Implementing conversation history, user preferences, and contextual memory across sessions requires a distributed cache layer, a session database, and careful thread management.

### 4. Cost Unpredictability

Without proper infrastructure, compute costs spiral out of control. Self-hosted vector databases, GPU instances for embedding generation, always-on API servers, and logging infrastructure can run tens of thousands of dollars per month before your product even generates revenue.

### 5. Integration Fragmentation

Connecting LLMs, vector stores, memory systems, monitoring, and APIs requires stitching together dozens of services and managing complex dependency chains. Each integration point is a potential failure mode, a versioning headache, and a security surface that needs patching.

### 6. Observability Gaps

Production AI systems are black boxes without proper instrumentation. Understanding agent behavior, debugging reasoning failures, and tracing tool call chains all require comprehensive logging and monitoring infrastructure that takes significant time to build correctly.

---

## Why AWS Bedrock AgentCore?

AWS Bedrock AgentCore solves these challenges by providing a **unified, managed platform** for enterprise agentic AI.

| Challenge | Traditional Approach | AgentCore Solution |
|-----------|---------------------|-------------------|
| **Infrastructure** | Manage EC2, ECS, K8s clusters | Serverless deployment with `agentcore deploy` |
| **Scalability** | Manual load balancing, auto-scaling config | Automatic scaling built into Bedrock runtime |
| **Memory** | Build custom DynamoDB/Redis solutions | Native `AgentCoreMemorySaver` and `AgentCoreMemoryStore` |
| **Cost** | Pay for idle instances 24/7 | Pay-per-invocation pricing model |
| **Monitoring** | Set up CloudWatch, X-Ray manually | Automatic CloudWatch integration out of the box |
| **Security** | Manage IAM policies, VPCs, secrets manually | Integrated AWS Secrets Manager and IAM roles |
| **Deployment** | Write Dockerfiles, push to ECR, update ECS tasks | Single command: `agentcore deploy` |

### AgentCore Capabilities

![AgentCore Capabilities](docs/images/7a%20Amazon%20Bedrock%20AgentCore%20Capabilities.png)

---

## Project Architecture

This project implements a three-tier architecture optimized for enterprise deployments.

```
+--------------------------------------------------+
|                  Frontend Layer                  |
|  React UI (Port 3000)                            |
|  - Chat Interface with session management        |
|  - Real-time streaming responses                 |
+--------------------------------------------------+
                        |
               HTTP / REST API
                        |
+--------------------------------------------------+
|             Application Layer (AWS)              |
|  Bedrock AgentCore Runtime                       |
|  - Agent Orchestration (LangGraph)               |
|  - Tool Execution Engine (3 specialized tools)   |
|  - Memory Management (short + long term)         |
|  LLM: ChatGroq (openai/gpt-oss-20b)             |
|  Embeddings: Bedrock Titan Text v2               |
+--------------------------------------------------+
                        |
+--------------------------------------------------+
|                   Data Layer                     |
|  FAISS Vector Store  |  AgentCore Memory Store   |
|  (FAQ embeddings)    |  (Conversation history)   |
|  CloudWatch Logs     |  AWS Secrets Manager      |
+--------------------------------------------------+
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React + Vite | Chat interface |
| **Backend** | FastAPI (Python 3.11+) | API server |
| **Agent Framework** | LangChain + LangGraph | Agent orchestration |
| **LLM** | Groq API (openai/gpt-oss-20b) | Language model |
| **Embeddings** | Amazon Bedrock Titan Text v2 | Vector generation |
| **Vector Store** | FAISS | Semantic search |
| **Memory** | AWS AgentCore Memory Store | Conversation persistence |
| **Deployment** | AWS Bedrock AgentCore Runtime | Serverless hosting |
| **Monitoring** | AWS CloudWatch | Logs and metrics |

---

## Key Features

### 1. Intelligent Semantic Search

Uses Amazon Bedrock Titan Embeddings to convert FAQ entries into high-dimensional vectors, enabling semantic similarity search that goes far beyond keyword matching.

### 2. Multi-Tool Agent Architecture

The agent has access to three specialized tools:

- `search_faq` - Quick 3-result search for straightforward questions
- `search_detailed_faq` - Extended 5-result search for complex, multi-part questions
- `reformulate_query` - Aspect-focused reformulation for pricing, activation, or troubleshooting queries

### 3. Persistent Memory System

- **Short-term Memory**: `AgentCoreMemorySaver` maintains full conversation context within a session
- **Long-term Memory**: `AgentCoreMemoryStore` preserves user preferences and interaction patterns across sessions
- **Session Management**: Thread-based conversation tracking with unique session IDs

### 4. Production-Grade Secret Management

- Graceful fallback from AWS Secrets Manager to environment variables
- Secrets never appear in code or logs
- Supports both local development and production without code changes

### 5. Zero-Infrastructure Deployment

```bash
agentcore deploy
```

---

## Prerequisites

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Node.js 20+** for frontend development
- **AWS Account** with appropriate permissions
- **Groq API Key** ([Get yours at console.groq.com](https://console.groq.com/))
- **AWS CLI** ([Installation Guide](https://aws.amazon.com/cli/))

---

## Step-by-Step Deployment Guide

### 1. Environment Setup

#### Step 1.1: Get API Keys

You will need a HuggingFace token if you plan to use HuggingFace models:

![Create HuggingFace Token](docs/images/1%20create%20huggingface%20token.png)

#### Step 1.2: Clone and Install

```bash
git clone https://github.com/manuelbomi/bedrock_repo.git
cd bedrock_repo

# Install with pip
pip install -e .

# Or with uv (faster)
uv pip install -e .
```

Dependencies managed in `pyproject.toml`:

- `bedrock-agentcore>=1.0.7` - Core AgentCore runtime
- `bedrock-agentcore-starter-toolkit>=0.2.0` - CLI tooling
- `langchain`, `langchain-aws`, `langchain-groq`, `langgraph` - Agent framework
- `faiss-cpu>=1.13.0` - Vector search
- `boto3>=1.28.0` - AWS SDK
- `langgraph-checkpoint-aws>=0.1.0` - AWS-backed memory

![Bedrock AgentCore Platform](docs/images/4%20amazon%20bedrock%20agentcore.png)

---

### 2. AWS Configuration

#### Step 2.1: Install AWS CLI

![Install AWS CLI](docs/images/3%20install%20AWS%20CLI.png)

Download and install the AWS CLI from [aws.amazon.com/cli](https://aws.amazon.com/cli/).

#### Step 2.2: Create an IAM User

Navigate to the IAM Console and create a new user with programmatic access.

![Create IAM User Step 1](docs/images/5%20Create%20IAM%20User.png)

![Create IAM User Step 2](docs/images/5b%20Create%20IAM%20User%20to%20be%20able%20to%20log%20into%20AWS.png)

#### Step 2.3: Assign Permissions

Create a permissions group with the following policies:

- `AdministratorAccess`
- `AmazonBedrockFullAccess`
- `CodeBuildAdminAccess`
- `AmazonBedrockAgentCoreFullAccess`

![Create Permissions Group](docs/images/create%20a%20group%20wt%20AdminAccess%20AmazonBedrockFullAccess%20CodebuildAdminAccess%20BedrockAgentCoreFullAccess%20and%20select%20the%20group.png)

![Add User to Group Step 1](docs/images/5c%20Add%20teh%20User%20to%20a%20Group.png)

![Add User to Group Step 2](docs/images/5d%20Add%20the%20User%20to%20a%20group.png)

![Confirm User Creation](docs/images/5e%20Create%20User.png)

#### Step 2.4: Generate Access Keys

![Save User Credentials](docs/images/6%20Save%20URL%20Username%20Password%20for%20the%20created%20user%20and%20then%20click%20on%20the%20user.png)

![Create CLI Access Keys](docs/images/6b%20click%20create%20access%20keys%20and%20select%20CLI.png)

![Copy Access and Secret Keys](docs/images/6e%20copy%20the%20Access%20Key%20and%20Secrte%20Access%20key%20of%20ur%20IAM%20USer%20and%20go%20to%20your%20local%20powershell%20and%20type%20aws%20configure%20and%20input%20the%20parameters.png)

#### Step 2.5: Configure the AWS CLI

```bash
aws configure
```

```
AWS Access Key ID:     [paste your Access Key ID]
AWS Secret Access Key: [paste your Secret Access Key]
Default region name:   us-east-1
Default output format: json
```

---

### 3. API Keys Setup

#### Step 3.1: Why Groq? — The LPU Advantage

Groq is not just another LLM API. It is built on a fundamentally different hardware architecture called the **Language Processing Unit (LPU)**.

Standard LLM inference runs on GPUs, which are optimized for parallel matrix operations across thousands of cores. That works well for training, but auto-regressive text generation is an inherently **sequential process** — each token must be generated before the next one can start. GPUs are therefore underutilized during inference and face a significant **memory bandwidth bottleneck**: the model weights must be loaded from HBM (high-bandwidth memory) on every single token generation step.

Groq's LPU eliminates this bottleneck by using **on-chip SRAM** — the weights stay resident on the chip and do not need to be reloaded from external memory for each token. The result is inference speeds that are **10x to 20x faster** than equivalent GPU-based services, with dramatically lower and more predictable latency.

**Why this matters for agentic systems specifically:**

In a standard chatbot, slow inference is annoying. In an agentic system, it is catastrophic. Each agent "turn" involves:

1. Calling the LLM to decide which tool to use
2. Executing the tool (FAISS search in our case)
3. Calling the LLM again to interpret the tool result
4. Generating the final response

That is **2–3 LLM calls per user message**. With a slow inference backend, a single question could take 15–30 seconds. With Groq, each LLM call completes in under a second, making the agent feel genuinely responsive even in production.

Groq also provides access to powerful open-source models (this project uses `openai/gpt-oss-20b`) at a fraction of the cost of proprietary APIs.

#### Step 3.2: Get Your Groq API Key

Groq provides extremely fast inference for open-source models at very low cost.

![Create Groq API Key](docs/images/2%20create%20Groq%20API%20Keys.png)

![Groq Computation Harness](docs/images/8c%20Groq%20computation%20Harness.png)

#### Step 3.3: Create the `.env` File

```bash
GROQ_API_KEY=your_groq_api_key_here
AWS_REGION=us-east-1
```

In production, the Groq API key is retrieved from AWS Secrets Manager automatically. No `.env` file is needed on the deployed container.

---

### 4. Agent Configuration

#### Step 4.1: Build the FAISS Vector Index

```bash
python build_faiss_index.py
```

This script:

1. Loads `buy_n_sell.csv` - 97 FAQ question-and-answer pairs
2. Formats each row as `"Q: {question}\nA: {answer}"`
3. Calls Amazon Bedrock Titan Text Embeddings v2
4. Saves the FAISS index to `./faiss_index/`

#### Step 4.2: Create Your AgentCore Runtime File

Wrap your agent with `BedrockAgentCoreApp`:

![Create Local AgentCore Instance](docs/images/8%20create%20a%20replica%20of%20the%20original%20python%20file%20for%20bedrock%20runtime%20and%20create%20an%20instance%20of%20bedrock%20runtime%20on%20the%20file%20locally.png)

The `@app.entrypoint` decorator marks the function AgentCore will call on each invocation:

![AgentCore App Entrypoint](docs/images/8b%20agentcore%20app%20entrypoint%20in%20local%20code.png)

#### Step 4.3: Run AgentCore Configure

```bash
agentcore configure -e ./02_agentcore_memory.py
```

This launches an interactive wizard that reads your Python file and creates `.bedrock_agentcore.yaml`:

![AgentCore Configure Command](docs/images/9%20agentcore%20invocation%20on%20local%20file.png)

![YAML Configuration Created](docs/images/9b%20so%20agentecore%20will%20use%20the%20agentcore%20configure%20-e%2001_agentcore_runtime.py%20command%20in%209%20to%20create%20a%20yaml%20file%20to%20run%20the%20local%20file.png)

![YAML in Repository](docs/images/9c%20so%20the%20agentcore%20command%20in%209%20and%209a%20has%20been%20used%20to%20create%20a%20yaml%20file%20in%20the%20local%20code%20repo.png)

![YAML File Contents](docs/images/9d%20so%20the%20yaml%20file%20is%20created.png)

#### Step 4.4: Test Locally

```bash
agentcore launch --env GROQ_API_KEY="your_groq_api_key_here"
```

---

### 5. Deployment to AWS

#### Step 5.1: Deploy the Agent

```bash
agentcore deploy
```

This single command packages your code, builds a Docker container, pushes it to ECR, and deploys it to AWS Bedrock AgentCore with auto-scaling and CloudWatch logging fully configured.

![Agent Successfully Deployed on AWS](docs/images/10%20The%20deployed%20agent%20on%20AWS.png)

#### Step 5.2: Invoke the Deployed Agent

```bash
# JSON syntax
agentcore invoke "{\"prompt\": \"What does DataNivra do?\"}"

# Single-quote syntax
agentcore invoke "{'prompt': 'How do I create an account?'}"
```

![Invoke Deployed Agent Step 1](docs/images/10a%20Now%20invoke%20the%20deployed%20agent.png)

![Invoke Deployed Agent Step 2](docs/images/10b%20Now%20invoke%20the%20deployed%20agent.png)

![Successful Invocation Response](docs/images/13h%20agentcore%20invocation%20now%20works.png)

#### Step 5.3: Monitor with CloudWatch

All `print()` statements in the agent are automatically captured in CloudWatch Logs.

![CloudWatch Logs Dashboard](docs/images/11%20Cloudwatch.png)

---

### 6. Memory Configuration

AgentCore provides a three-tier memory system that makes your agent genuinely stateful across conversations, users, and sessions.

#### Step 6.1: Create a Memory Store

Navigate to the Amazon Bedrock console and create a new memory resource:

![Create Memory for Agent Step 1](docs/images/12%20Create%20memory%20for%20your%20agent.png)

![Create Memory for Agent Step 2](docs/images/12b%20Create%20memory%20for%20your%20agent.png)

Save the memory ID - you will need it in your agent code.

#### Step 6.2: Configure Memory Strategies

##### Memory Summarization

![Add Memory Strategy](docs/images/12c%20Add%20memory%20strategy.png)

![Choose Memory Summarization](docs/images/12d%20choose%20memory%20summarization%20to%20preserve%20important%20contexts.png)

Automatically condenses long conversation histories while preserving essential context.

##### Semantic Memory

![Add Semantic Memory](docs/images/12e%20Add%20semantic%20memory.png)

Stores factual information the user has shared across sessions - account details, product preferences, prior issues.

##### Episode Memory

![Add Episode Memory](docs/images/12f%20Add%20episode%20memory.png)

Records specific past interactions - what problems were solved, what steps were taken.

##### User Preference Memory

![Add User Preference Memory](docs/images/12g%20Add%20user%20preference%20memory.png)

Tracks behavioral patterns - preferred response style, language, level of technical detail.

#### Step 6.3: Verify Memory Configuration

![Check Memory Details](docs/images/12h%20click%20to%20check%20memory%20details.png)

#### Step 6.4: Deploy the Memory-Enabled Agent

```bash
agentcore configure -e ./02_agentcore_memory.py
```

![Configure Memory Agent Step 1](docs/images/13%20Deploy%20agent%20with%20memory%20by%20using%20the%2003_agent%20file%20and%20deploy%20with%20agentcore%20configure%20command.png)

![Configure Memory Agent Step 2](docs/images/13b%20Deploy%20agent%20with%20memory%20by%20using%20the%2003_agent%20file%20and%20deploy%20with%20agentcore%20configure%20command%20select%201%20here.png)

![Configuration Success](docs/images/13c%20agent%20with%20memory%20configuration%20success.png)

```bash
agentcore launch --env GROQ_API_KEY="your_groq_api_key_here"
```

![Launch with Groq Key](docs/images/13d%20Now%20launch%20with%20my%20grok%20key.png)

```bash
agentcore deploy
```

![Memory-Enabled Container Deployed](docs/images/13e%20container%20wt%20memory%20deployed%20to%20Bedrock.png)

![Agent with Memory on Amazon Bedrock](docs/images/13f%20agent%20with%20memory%20on%20Amazon%20Bedrock.png)

![CloudWatch Deployment Logs](docs/images/14%20Cloudwatch%20logs.png)

---

## Code Architecture Deep Dive

### `02_agentcore_memory.py` - The Production Agent

This is the single file that runs as your deployed agent. It is self-contained: memory initialization, vector index loading, tool definitions, LLM configuration, agent construction, and the AgentCore entrypoint - all in under 285 lines.

#### Section 1: Imports and Application Initialization (Lines 1-20)

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from langgraph_checkpoint_aws import AgentCoreMemorySaver, AgentCoreMemoryStore

app = BedrockAgentCoreApp()
```

`BedrockAgentCoreApp` is the container that AgentCore wraps around your code. It handles the HTTP server, request routing, graceful shutdown, and CloudWatch integration automatically. You never write any of that yourself.

`AgentCoreMemorySaver` and `AgentCoreMemoryStore` are LangGraph-compatible implementations backed by AWS-managed storage rather than local memory or a self-hosted database.

#### Section 2: Memory Initialization (Lines 22-30)

```python
MEMORY_ID = "agent_FAQ_memory-1miyurA534"

# Short-term: maintains conversation context within a session
checkpointer = AgentCoreMemorySaver(memory_id=MEMORY_ID)

# Long-term: remembers user personality and preferences across sessions
store = AgentCoreMemoryStore(memory_id=MEMORY_ID)
```

The same `MEMORY_ID` links both components to the memory resource created in the AWS console. Under the hood, AgentCore manages DynamoDB tables and handles serialization, TTL, and access control.

Key distinction:

- `checkpointer` - tied to a `thread_id`, scoped to a session
- `store` - tied to a `user_id` / `actor_id`, persists indefinitely across sessions

#### Section 3: Secret Management (Lines 33-48)

```python
def get_secret(secret_name: str, region_name: str = "us-east-1") -> str:
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)
    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        return secret.get('GROQ_API_KEY')
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        raise

# Try env var first (local dev), fall back to Secrets Manager (production)
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or get_secret("bedrock-agentcore/groq-api-key", REGION)
```

The `.env` file is never deployed. The deployed container uses Secrets Manager exclusively. This single function makes the codebase work identically in both environments.

#### Section 4: FAISS Vector Store (Lines 51-69)

```python
emb = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0", region_name="us-east-1")

FAISS_INDEX_PATH = "./faiss_index"
faq_store = FAISS.load_local(FAISS_INDEX_PATH, emb, allow_dangerous_deserialization=True)
```

The FAISS index is loaded once at startup, not rebuilt on every request. This keeps cold start times low and embedding costs minimal - you pay for embeddings only once at index build time.

#### Section 5: The Three Agent Tools (Lines 72-143)

**Tool 1: `search_faq`** - Primary tool for most queries

```python
@tool
def search_faq(query: str) -> str:
    """Search the FAQ knowledge base for relevant information.
    Use this when the user asks questions about products, services, or policies."""
    results = faq_store.similarity_search(query, k=3)
```

**Tool 2: `search_detailed_faq`** - For complex or multi-part questions

```python
@tool
def search_detailed_faq(query: str, num_results: int = 5) -> str:
    """Search with more results for complex queries.
    Use when the initial search does not provide enough information."""
    results = faq_store.similarity_search(query, k=num_results)
```

**Tool 3: `reformulate_query`** - For aspect-focused retrieval

```python
@tool
def reformulate_query(original_query: str, focus_aspect: str) -> str:
    """Reformulate the query to focus on a specific aspect like pricing,
    activation, or troubleshooting."""
    reformulated = f"{focus_aspect} related to {original_query}"
    results = faq_store.similarity_search(reformulated, k=3)
```

Three tools mirrors the retrieval chain a skilled support agent would follow: start broad, go deeper if needed, then zoom into a specific aspect if still unclear.

#### Section 6: The System Prompt (Lines 154-247)

A 93-line system prompt that defines the agent's persona, retrieval strategy, response format, and behavior in edge cases. Key rules:

- Always call `search_faq` first; escalate only if results are insufficient
- Never invent policies, prices, procedures, or technical details
- Direct answer first, supporting details second, next steps third
- If the knowledge base does not have the answer, say so explicitly

#### Section 7: Agent Creation with Memory (Lines 249-256)

```python
agent = create_agent(
    model=model,
    tools=tools,
    checkpointer=checkpointer,   # This single line enables memory
    system_prompt=system_prompt
)
```

Passing `checkpointer` to `create_agent` turns a stateless Q&A tool into a stateful conversational agent. Without it, every message is treated as the start of a new conversation.

#### Section 8: The AgentCore Entrypoint (Lines 259-285)

```python
@app.entrypoint
def agent_invocation(payload, context):
    query = payload.get("prompt", "No prompt found in input")

    # Prefer session_id from AgentCore context, fall back to payload
    thread_id = (
        context.session_id
        if hasattr(context, 'session_id') and context.session_id
        else payload.get("session_id", "default-session")
    )

    config = {"configurable": {"thread_id": thread_id, "actor_id": "default"}}

    result = agent.invoke(
        {"messages": [("human", query)]},
        config=config
    )

    return {"response": result["messages"][-1].content}
```

`thread_id` is the key to memory isolation. Each unique `thread_id` maintains its own independent conversation history. In a multi-user deployment, the frontend generates a UUID per user session and passes it with every request.

---

## Vector Database Strategy

### Why FAISS for This Project?

This project uses **FAISS** (Facebook AI Similarity Search) as the vector store. It is the right tool for this specific use case.

#### Where FAISS Excels

| Property | Detail |
|----------|--------|
| **Speed** | Sub-millisecond similarity search for datasets under 1M vectors |
| **Zero infrastructure** | No server to deploy, monitor, or patch |
| **Cold start** | `FAISS.load_local()` takes under 100ms |
| **Cost** | Entirely free - no database licensing or hosting fees |
| **Portability** | The index is a file; it moves with your container |

For 97 FAQ entries, FAISS is not just "good enough" - it is the optimal choice.

#### When FAISS Becomes a Liability at Enterprise Scale

| Enterprise Requirement | FAISS Limitation | Better Alternative |
|------------------------|------------------|--------------------|
| Concurrent updates from multiple services | Requires full index rebuild | pgvector, Weaviate |
| High availability and replication | Single file, single point of failure | Milvus, Weaviate Cloud |
| Compliance audit logging | No access logs or change history | pgvector with PostgreSQL audit |
| Scaling to millions of vectors | Memory limits and performance degradation | Milvus, Pinecone |
| Real-time index updates without downtime | Not supported | Weaviate, Qdrant |
| Multi-tenant access control | Not supported | pgvector with row-level security |

#### Migration Path: pgvector

```python
from langchain_postgres import PGVector

vector_store = PGVector(
    connection_string="postgresql://user:pass@host:5432/db",
    embedding_function=emb,
    collection_name="faq_embeddings"
)
```

Adds vector search to a PostgreSQL database with full ACID guarantees, SQL metadata filtering, and audit logging.

#### Migration Path: Weaviate

```python
from langchain_weaviate import WeaviateVectorStore

vector_store = WeaviateVectorStore(
    client=weaviate_client,
    index_name="FAQ",
    text_key="content",
    embedding=emb
)
```

Adds hybrid search (BM25 + vector), a GraphQL API, and a cloud-hosted option.

#### Decision Framework

| Scale | Recommendation |
|-------|---------------|
| Up to ~100k vectors, single-service | **FAISS** - simple, fast, free |
| 100k to 10M vectors, multiple teams | **pgvector** - SQL integration, ACID, audit logs |
| 10M+ vectors, multi-region | **Milvus** - purpose-built, horizontally scalable |
| Want modern API + hybrid search | **Weaviate** - developer-friendly, production-ready |

---

## Frontend Integration

### React Chat Interface

The project ships with a production-ready React frontend:

![React Frontend View 1](docs/images/1a%20React%20Front%20end.png)

![React Frontend View 2](docs/images/1b%20React%20Front%20end.png)

### Quick Start

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

The frontend maintains a `session_id` stored in `localStorage` and passes it with every API request. The backend uses it as the LangGraph `thread_id`, keeping each user's conversation history isolated.

---

## Production Considerations

### Security Best Practices

**API Key Management**

```python
# Handles both local (.env) and production (Secrets Manager) environments
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or get_secret("bedrock-agentcore/groq-api-key")
```

**IAM Least Privilege** - Before going to production, narrow the IAM permissions to only what AgentCore needs:

- `bedrock:InvokeModel` for the embedding model
- `secretsmanager:GetSecretValue` for the API key secret
- `logs:CreateLogGroup`, `logs:PutLogEvents` for CloudWatch
- `ecr:GetAuthorizationToken`, `ecr:PutImage` for container push

### Cost Optimization

| Component | When You Pay | How to Reduce Cost |
|-----------|-------------|-------------------|
| **Bedrock Titan Embeddings** | Per 1,000 tokens at index build time | Build index once; cache aggressively |
| **AgentCore Runtime** | Per invocation + duration | Batch concurrent requests |
| **Groq API** | Per million tokens | Use `temperature=0` for deterministic caching |
| **CloudWatch Logs** | Per GB ingested and stored | Set 30-day retention; filter debug logs |

### Monitoring

```python
# These print statements are automatically captured in CloudWatch
print(f"[TOOL] search_faq called with: {query}")
print(f"[TOOL] Found {len(results)} results")
print(f"[SESSION] thread_id={thread_id}")
```

Set up CloudWatch Alarms on:

- Error rate exceeding 1% over 5 minutes
- P95 latency exceeding 5 seconds
- Invocation count dropping to zero (agent down)

---

## Troubleshooting

### "FAISS index not found"

Run `python build_faiss_index.py` and ensure `faiss_index/` is not in `.gitignore`.

### "GROQ_API_KEY not found"

Check `.env` for local runs. For deployed agents, verify the secret name in Secrets Manager matches the string passed to `get_secret()`.

### "CloudWatch logs not appearing"

Ensure the IAM role has `logs:CreateLogGroup`, `logs:CreateLogStream`, and `logs:PutLogEvents`.

### "Memory not persisting across sessions"

Ensure the frontend passes a stable `session_id` and that `agent_invocation` extracts it from `context.session_id` or `payload["session_id"]`.

### "Agent giving inconsistent or hallucinated answers"

Rebuild the FAISS index if FAQ data has changed. Verify the system prompt includes: "Never invent policies, prices, procedures, or technical details."

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **AWS Bedrock Team** for the AgentCore platform
- **LangChain / LangGraph** for the agent orchestration framework
- **Groq** for fast open-source LLM inference
- **Meta AI Research** for FAISS

---


### Thank you for reading

#### Please consider giving a star if you find the repo useful. Thank you.

---

### **AUTHOR'S BACKGROUND**
### Author's Name:  Emmanuel Oyekanlu
```
Skillset:   I have experience spanning several years in data science, enterprise AI architecture and solutions, developing scalable enterprise data pipelines,
enterprise solution architecture, architecting enterprise systems data and AI applications,
software and AI solution design and deployments, data engineering, industrial intelligent vision systems, high performance computing (GPU, CUDA), machine learning,
NLP, Agentic-AI and LLM applications as well as deploying scalable solutions (apps) on-prem and in the cloud.

I can be reached through: manuelbomi@yahoo.com

Website: https://www.emmanueloyekanlu.com/
Publications:  https://scholar.google.com/citations?user=S-jTMfkAAAAJ&hl=en
LinkedIn:  https://www.linkedin.com/in/emmanuel-oyekanlu-6ba98616
Github:  https://github.com/manuelbomi

```
[![Icons](https://skillicons.dev/icons?i=aws,azure,gcp,scala,mongodb,redis,cassandra,kafka,anaconda,matlab,nodejs,django,py,c,anaconda,git,github,mysql,docker,kubernetes&theme=dark)](https://skillicons.dev)



