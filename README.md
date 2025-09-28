# Mongolian Legal AI Agent

A ReAct agent powered by OpenAI that provides specialized assistance with legal questions, particularly focusing on **Mongolian Private Data Protection Law** (https://legalinfo.mn/mn/detail?lawId=16390288615991). The agent uses vector search and web search capabilities to deliver accurate, contextual legal guidance.

## Overview

This project implements an intelligent legal assistant that:
- Uses an OpenAI model for natural language understanding and generation
- Employs ReAct (Reasoning and Acting) methodology for iterative problem-solving
- Searches through legal documents in Weaviate vector database
- Supplements knowledge with real-time web search
- Specializes in Mongolian data protection legislation

## Architecture

```
.
├── agent.py                    # Main ReAct agent implementation
├── docker-compose.yml          # Docker services configuration
├── Dockerfile                  # Container definition
├── docs/                       # Legal documents
├── src/                        # Core application modules
│   ├── database_management.py  # Database operations
│   ├── mcp_client.py           # MCP protocol client
│   └── weaviate_server.py      # MCP server using DB operations
├── tests/                      # Testing utilities
├── utils/                      # Helper functions
│   ├── document_management.py  # Document preprocessing for insertion
│   └── model_management.py     # Model connection/generation
└── requirements.txt
```

## Features

- **Intelligent Legal Q&A**: Specialized responses to Mongolian legal queries
- **Vector Search**: Semantic search through legal documents using BGE-m3 embeddings
- **Web Search Integration**: Real-time information retrieval via Google Search
- **Multi-modal Processing**: Handles various document formats

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- NVIDIA GPU (for embedding server)
- OpenAI API key
- Google Search API credentials (as in https://github.com/mixelpixx/Google-Search-MCP-Server)

## Setup

### 1. Environment Variables

Create a `.env` file with the following variables:

```env
MODEL_NAME=chatgpt-4o-latest
EMBEDDING_SERVER=http://localhost:8080
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Required Services

#### Start Weaviate Database Server somewhere

```docker
services:
  weaviate:
    command:
    - --host
    - 0.0.0.0
    - --port
    - '8080'
    - --scheme
    - http
    image: cr.weaviate.io/semitechnologies/weaviate:1.32.1
    ports:
    - 8080:8080
    - 50051:50051
    volumes:
    - weaviate_data:/var/lib/weaviate
    restart: on-failure:0
    environment:
      QUERY_DEFAULTS_LIMIT: 25
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'true'
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      ENABLE_API_BASED_MODULES: 'true'
      CLUSTER_HOSTNAME: 'node1'
volumes:
  weaviate_data:
```

```bash
docker-compose up -d
```

#### Start BGE-m3 Embedding Server (local or remote)
```bash
model=BAAI/bge-m3
volume=$PWD/data
docker run --gpus all -p 8080:80 -v $volume:/data --pull always ghcr.io/huggingface/text-embeddings-inference:latest --model-id $model
```

### 4. Insert the document into the vector database 
```bash
python src/insert_documents.py
```
This will create the collection (in other words, a table) in your database if it doesn't exist according to the schema for the legal documents.

### 5. Run the Agent
```bash
python agent.py
```

This will create an indefinite cycle where your queries are processed through a series of agentic tool calls and reasoning steps.

## Dependencies

```
python-docx
langchain
langchain-community
weaviate-client
mcp[cli]
langchain-mcp-adapters
openai
python-dotenv
jinja2
```

## MCP Server Configuration

The agent configures two MCP (Model Context Protocol) servers:

1. **Weaviate Vector Database**: Handles document search and retrieval (`src/weaviate_server.py`)
2. **Google Search**: Provides web search capabilities

Configuration is handled automatically in `agent.py` using the environment variables provided.

## Usage

Once all services are running, interact with the agent through the command line interface. Ask questions about Mongolian data protection law or other legal topics, and the agent will:

1. Search relevant legal documents in the vector database
2. Supplement with web search if needed
3. Provide comprehensive, contextual answers
4. Iterate on responses using the ReAct methodology

## Testing

The `tests/` directory contains utilities for:
- Document insertion and deletion
- Embedding functionality testing
- Document management operations (like querying)

## License

See `License` file for details.

## Contributing

This project specializes in Mongolian legal assistance. Contributions should focus on improving legal accuracy, expanding document coverage, or enhancing the AI's reasoning capabilities.