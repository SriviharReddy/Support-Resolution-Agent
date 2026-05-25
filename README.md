# 🎯 Support Resolution Agent

A support-issue diagnosis agent using tool-based reasoning with LangGraph structured flows to classify urgency, fill missing info, select resolution steps, and escalate to humans when required.

Designed as a minimal viable product (MVP) / proof of concept (POC), it implements a highly-structured and robust five-step reasoning flow powered by **Amazon Bedrock (Nova Lite)**.

---

## 🏗️ Structured Graph Workflow

The agent structures its support operations into a clean, predictable pipeline incorporating smart routing and human-in-the-loop triggers:

```
[START]
   │
   ▼
1. ⚡ Classify Urgency ──► Evaluates user text and maps issue priority
   │                      (critical, high, medium, low) using Bedrock
   ▼
2. 🔍 Check Context   ──► Checks if Customer ID is present. If missing, requests
   │                      ID directly and halts; otherwise proceeds.
   ▼
3. 🔧 Diagnose &      ──► Invokes tools (lookup CRM details, consult tech KB)
   │   Resolve            and drafts a resolution response.
   │
   ├─► [Yes: Priority is Critical] ──► 👤 4. Human Escalation (Interrupt)
   │                                           (Wait for agent approval/edits)
   │                                                    │
   └─► [No] ──────────────────────────►                 │
                                                        ▼
                                           📤 5. Deliver Response
                                                        │
                                                        ▼
                                                     [END]
```

1. **Classify Urgency (`classify_urgency`)**: Evaluates incoming customer inquiries to automatically classify the priority score.
2. **Check Context (`check_context`)**: Inspects context. If vital information (like Customer ID) is missing, it asks the customer directly and safely halts the flow until resolved.
3. **Diagnose & Resolve (`diagnose_and_resolve`)**: Utilizes tool-based searches (`lookup_customer` and `search_knowledge_base`) to gather details and generate a resolution draft.
4. **Human Escalation (`human_escalation`)**: Employs a secure LangGraph **`interrupt`** mechanism to pause execution and allow human support agents to approve or modify responses before delivery.
5. **Deliver Response (`deliver_response`)**: Deliver final responses and commits changes.

---

## 📁 Recommended Directory Structure

The repository follows the official recommended structure for scalable LangGraph applications:

```
Support-Resolution-Agent/
├── my_agent/                  # Main package containing graph logic
│   ├── utils/                 # Modular graph subcomponents
│   │   ├── __init__.py
│   │   ├── state.py           # Core state definition (priority, context, steps)
│   │   ├── tools.py           # Support tools (lookup_customer, search_knowledge_base)
│   │   └── nodes.py           # Node logic utilizing Amazon Bedrock
│   ├── __init__.py
│   └── agent.py               # Graph construction & compilation
├── .env                       # Local environment configurations (ignored by git)
├── .env.example               # Reference template for configurations
├── langgraph.json             # Deployment CLI configuration file
├── pyproject.toml             # uv package and dependency metadata
└── app.py                     # Premium Streamlit UI with progress logs and human review panels
```

---

## 🛠️ Support Tools

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `lookup_customer` | `customer_id` | Looks up customer metadata (account name, tier, and status) from the CRM system. |
| `search_knowledge_base` | `query` | Searches the technical knowledge base (passwords, billing, refunds, connection errors). |

---

## 🚀 Quick Start

### 📋 Prerequisites
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (fast Python package manager)
- AWS credentials with access to **Amazon Bedrock (Nova Lite)**

### 💻 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/SriviharReddy/Support-Resolution-Agent.git
   cd Support-Resolution-Agent
   ```

2. **Configure your environment**
   Copy the example environment file and insert your AWS Bedrock keys:
   ```bash
   cp .env.example .env
   ```
   *Edit `.env` and fill in:*
   ```env
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_DEFAULT_REGION=us-east-1
   BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
   ```

3. **Run the Streamlit Application**
   Running via `uv` automatically sets up the virtual environment, resolves all dependencies from `pyproject.toml`, and launches the web page:
   ```bash
   uv run streamlit run app.py
   ```

---

## 🎨 Premium Frontend Features

The Streamlit frontend (`app.py`) provides an immersive, interactive support cockpit:
- **HSL-tailored dark gradient backgrounds** with premium glassmorphic accents.
- **Node progress monitoring**: Live checklist in the sidebar displaying active workflow states (`Classify Urgency`, `Context Validation`, `Diagnostic Tools`, `Human Escalation`, `Deliver Response`).
- **Human Escalation Review Panel**: Integrated form allowing human agents to inspect diagnostic contexts, review proposed drafts, and approve or modify before pushing to the chat.
