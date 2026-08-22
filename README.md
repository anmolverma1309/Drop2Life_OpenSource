# Drop2Life_OpenSource

Drop2Life_OpenSource is an AI-powered onboarding navigator that acts as a "Digital Senior Mentor" for your codebase.

## Key Features
1. **Repository Ingestion & Visualization:** Deterministic parsing of Python ASTs to generate comprehensive visual dependency graphs.
2. **Issue-to-Code Mapping:** Hybrid Dense + Sparse Vector Search utilizing AWS Titan v2 and ChromaDB.
3. **Architectural Intent:** Analyzes historical Pull Requests via GitHub GraphQL and OpenRouter to explain *why* code exists. 
4. **The Indic Bridge (Jargon Buster):** LLM-powered mentor that simplifies technical jargon in English, Hindi, Tamil, Hinglish, etc.
5. **Environment Setup Guidance:** Scans repo configs to generate 1-click Bash/PowerShell setup scripts.
6. **Beginner Issue Matcher:** Identifies "Good First Issues" and flags if they are actively being worked on in other PRs.
7. **Drop2Life_OpenSource Architect (Agentic Onboarding):** End-to-end contribution planner that graphs blast-radiuses and reads terminal outputs.
8. **Personalized Feasibility Engine:** Repo gatekeeper and stateless User Profile context injection to ensure the AI speaks at the right skill level.

## System Architecture

```mermaid
flowchart LR
    %% User touchpoints
    U[Developer / Contributor] --> F[Frontend\nReact + TypeScript + Tailwind]
    F --> CLI[CLI Interface\nGraph Explorer\nTerminal Panel]
    F --> PAN[Panels\nCode Viewer\nArchitect\nIntent\nExplain]

    %% Frontend to backend flow
    CLI --> API[FastAPI Backend\nREST + async services]
    PAN --> API

    subgraph FE[Frontend Layer]
        F
        CLI
        PAN
    end

    subgraph BE[Backend Orchestration]
        API
        ING[Repository Ingestion]
        SEARCH[Issue-to-Code Search]
        EXPLAIN[Jargon Buster\nIndic Bridge]
        CHAT[Architect Agent\nContribution Planner]
        GATE[Gatekeeper\nFeasibility Engine]
        SETUP[Setup Generator]
    end

    subgraph DATA[Repo Intelligence Layer]
        GIT[GitHub Metadata\nGraphQL + Shallow Clone]
        META[Issues / PRs / Commits\nHistory + Context]
        PARSER[Parser + AST Analysis]
        GRAPH[Dependency Graph\nArchitecture Map]
        CHUNK[Chunked Code + Metadata]
        EMBED[AWS Bedrock\nTitan Embeddings]
        VEC[(ChromaDB\nVector Store)]
    end

    subgraph AI[LLM / Reasoning Layer]
        LLM[OpenRouter\nNemotron / LLM reasoning]
        RR[Repository Reasoning\nIssue solving guidance]
    end

    %% Ingestion flow
    API --> ING
    ING --> GIT
    GIT --> META
    META --> PARSER
    PARSER --> GRAPH
    GRAPH --> CHUNK
    CHUNK --> EMBED
    EMBED --> VEC

    %% Search and intelligence flow
    API --> SEARCH
    SEARCH --> VEC
    SEARCH --> META
    SEARCH --> RR

    API --> EXPLAIN
    EXPLAIN --> LLM

    API --> CHAT
    CHAT --> LLM
    CHAT --> META
    CHAT --> GRAPH

    API --> GATE
    GATE --> META
    GATE --> GRAPH

    API --> SETUP
    SETUP --> GIT
    SETUP --> META

    %% Outputs to user
    RR --> F
    GRAPH --> F
    SEARCH --> F
    EXPLAIN --> F
    CHAT --> F
    SETUP --> F

    classDef user fill:#0f172a,stroke:#94a3b8,color:#fff;
    classDef frontend fill:#1d4ed8,stroke:#bfdbfe,color:#fff;
    classDef backend fill:#0f766e,stroke:#99f6e4,color:#fff;
    classDef data fill:#9a5b00,stroke:#fcd34d,color:#fff;
    classDef ai fill:#7c3aed,stroke:#ddd6fe,color:#fff;

    class U user;
    class F,CLI,PAN frontend;
    class API,ING,SEARCH,EXPLAIN,CHAT,GATE,SETUP backend;
    class GIT,META,PARSER,GRAPH,CHUNK,EMBED,VEC data;
    class LLM,RR ai;
```

## How to Run the Project Locally

The project consists of a FastAPI backend and a Streamlit Tester UI. Both run from the `backend/` directory using Python 3.12.

### 1. Prerequisites
- Python 3.12 installed (`py -3.12 --version` on Windows)
- Git installed and on your PATH

### 2. First-Time Setup
Open your terminal and navigate to the backend directory:
```powershell
cd backend
```

Create a virtual environment and install dependencies:
```powershell
py -3.12 -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env`:
```powershell
cp .env.example .env
```
Open `.env` and add:
- `GITHUB_PAT`: Your GitHub Personal Access Token (prevents rate limits during ingestion)
- `OPENROUTER_API_KEY`: Required for Phase 2 AI features (OpenRouter Nemotron-3)
- `AWS_ACCESS_KEY_ID` & `AWS_SECRET_ACCESS_KEY`: Required for Phase 2 AI embeddings (AWS Titan v2)

---

### 4. Running the Servers

You need **two separate terminal windows**.

**Terminal 1 — Run the FastAPI Backend:**
```powershell
cd backend
.venv\Scripts\uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
*The API is now running at `http://127.0.0.1:8000`. You can view interactive docs at `http://127.0.0.1:8000/docs`.*

**Terminal 2 — Run the Streamlit Tester UI:**
```powershell
cd backend
.venv\Scripts\streamlit run tester\app.py --server.port 8501
```
*The UI will automatically open in your browser at `http://localhost:8501`. If you get ingestion errors, check the logs in Terminal 1.*