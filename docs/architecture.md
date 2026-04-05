# Architecture Overview

---

## Table of Contents

- [High-level diagram](#high-level-diagram)
- [Module breakdown](#module-breakdown)
- [Data flows](#data-flows)
- [Database schema](#database-schema)
- [Authentication flow](#authentication-flow)
- [Directory structure](#directory-structure)
- [Key design decisions](#key-design-decisions)

---

## High-level diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      React 18 Frontend                          │
│                                                                 │
│  Dashboard  ·  AI Systems  ·  Classification  ·  Documents      │
│  [Guard Scanner — coming]  ·  [RAG Chat — coming]              │
│                                                                 │
│  Zustand auth store  ·  TanStack Query  ·  Tailwind CSS         │
└──────────────────────────────┬──────────────────────────────────┘
                               │  REST/JSON  (axios + Bearer JWT)
┌──────────────────────────────▼──────────────────────────────────┐
│                    FastAPI Backend  /api/v1/                     │
│                                                                 │
│  ┌──────────────────┐  ┌───────────────┐  ┌─────────────────┐  │
│  │  Compliance      │  │  LLM Guard    │  │ RAG Intelligence│  │
│  │  Engine          │  │  Module       │  │ Module          │  │
│  │                  │  │               │  │                 │  │
│  │  /ai-systems     │  │  /guard/scan  │  │ /rag/query      │  │
│  │  /classification │  │  /guard/info  │  │ /rag/ingest*    │  │
│  │  /documents      │  │               │  │                 │  │
│  │                  │  │  1. Regex     │  │ FAISS index     │  │
│  │  Risk classifier │  │  2. DeBERTa   │  │ LangChain chain │  │
│  │  Doc templates   │  │  3. Decision  │  │ MLflow tracking │  │
│  │  EU AI Act rules │  │  4. Sanitizer │  │                 │  │
│  └────────┬─────────┘  └───────┬───────┘  └────────┬────────┘  │
│           │                    │                    │           │
│  ┌────────▼────────────────────▼────────────────────▼────────┐  │
│  │          Core: JWT Auth  ·  SQLAlchemy ORM  ·  Config     │  │
│  └───────────────────────────────┬────────────────────────────┘  │
└──────────────────────────────────┼──────────────────────────────┘
                                   │
              ┌────────────────────▼─────────────────┐
              │           PostgreSQL 15               │
              │  users · ai_systems · documents       │
              │  risk_assessments                     │
              └──────────────────────────────────────┘

* /rag/ingest not yet implemented — contributor opportunity
```

---

## Module breakdown

### Module 1 — Compliance Engine

Handles EU AI Act compliance tracking from system registration through document generation.

| File | Responsibility |
|---|---|
| `api/v1/ai_systems.py` | CRUD for AI system registry |
| `api/v1/classification.py` | Risk classification logic (Article 5, 6, 52 + Annex III) |
| `api/v1/documents.py` | Compliance document generation from templates |
| `models/ai_system.py` | `AISystem`, `RiskAssessment` ORM models |
| `models/document.py` | `Document` ORM model |
| `schemas/ai_system.py` | `RiskClassificationRequest`, questionnaire fields |

**Risk levels and their EU AI Act basis:**

| Level | EU AI Act basis | Examples |
|---|---|---|
| Unacceptable | Article 5 (prohibited) | Social scoring, real-time biometric ID in public spaces |
| High | Article 6 + Annex III | CV screening, credit scoring, medical devices, law enforcement |
| Limited | Article 52 (transparency) | Chatbots, deepfake generators, emotion recognition |
| Minimal | — | Spam filters, inventory management, video games |

---

### Module 2 — LLM Guard

A four-layer defence pipeline that runs on every prompt before it reaches an LLM. Designed to catch prompt injection, jailbreaks, and policy bypass attempts.

| File | Responsibility |
|---|---|
| `modules/guard/regex_rules.py` | Layer 1: fast regex heuristics, ~0ms |
| `modules/guard/intent_classifier.py` | Layer 2: DeBERTa-v3-small transformer, CPU ~200ms |
| `modules/guard/decision_engine.py` | Layer 3: combines regex + ML scores into a decision |
| `modules/guard/sanitizer.py` | Layer 4: removes meta-instructions from SANITIZE-level prompts |
| `modules/guard/llm_guard.py` | Orchestrator — runs all 4 layers in sequence |
| `modules/guard/guard_config.py` | Paths, thresholds, intent class mappings |
| `modules/guard/train.py` | Training script for fine-tuning the classifier |
| `api/v1/guard.py` | REST endpoint wrapping the pipeline |
| `notebooks/train_guard_classifier.ipynb` | Colab-ready fine-tuning notebook |

**Regex categories** (6 categories in `regex_rules.py`):

| Category | Examples | Severity |
|---|---|---|
| Instruction override | "ignore all previous instructions" | High |
| Role hijacking | "you are now DAN", "act as an evil AI" | High |
| Prompt disclosure | "repeat your system prompt", "show your instructions" | Medium |
| Policy bypass | "pretend you have no restrictions" | Medium |
| Dangerous code | `exec()`, `eval()`, `os.system()` patterns | Medium/High |
| Suspicious keywords | "jailbreak", "override", "bypass" | Low |

**Decision thresholds** (configurable in `.env`):

| Signal | Weight |
|---|---|
| Regex score | 0.4 |
| ML classifier score | 0.6 |
| Suspicious threshold | 0.5 → SANITIZE |
| Malicious threshold | 0.8 → BLOCK |

---

### Module 3 — RAG Intelligence

A retrieval-augmented generation pipeline that answers regulatory questions grounded in source documents.

| File | Responsibility |
|---|---|
| `modules/rag/document_loader.py` | Loads PDFs from local paths or S3, splits into chunks |
| `modules/rag/vector_store.py` | Builds and persists FAISS index; loads existing index |
| `modules/rag/retrieval_chain.py` | LangChain RetrievalQA chain (k=5 chunks) |
| `modules/rag/ml_flow.py` | MLflow query tracking stub |
| `api/v1/rag.py` | REST endpoints |

**Planned regulatory sources** (contributor opportunity):

- EU AI Act (Regulation EU 2024/1689)
- GDPR (Regulation EU 2016/679)
- ISO/IEC 42001:2023
- NIST AI RMF 1.0

---

## Data flows

### Guard scan pipeline

```
POST /api/v1/guard/scan
        │
        ▼
  JWT auth check
        │
        ▼
  LLMGuard.guard(prompt)
        │
        ├─► Layer 1: RegexFilter.check(prompt)
        │       Returns: flag (bool), score (0–1), matched_patterns
        │
        ├─► Layer 2: IntentClassifier.classify(prompt)
        │       Returns: intent (benign/suspicious/malicious), confidence
        │
        ├─► Layer 3: DecisionEngine.decide(regex_flag, regex_score, intent, confidence)
        │       Returns: decision (ALLOW/SANITIZE/BLOCK), reasoning
        │
        └─► Layer 4 (if SANITIZE): PromptSanitizer.sanitize(prompt)
                Returns: cleaned_prompt, changes_summary
                    │
                    ▼
              LLMClient.call(cleaned_prompt)  ← any OpenAI-compatible provider

Decision: BLOCK → return safe error message (no LLM call)
Decision: ALLOW → LLMClient.call(prompt)
Decision: SANITIZE → sanitize, then LLMClient.call(sanitized_prompt)
```

### Risk classification flow

```
POST /api/v1/classification/classify/{system_id}
        │
        ▼
  Receive RiskClassificationRequest
  (questionnaire answers — ~15 boolean fields)
        │
        ▼
  Check Article 5 prohibited uses
  (social scoring, real-time biometrics, subliminal manipulation)
        │
        ▼
  Check Annex III high-risk categories
  (HR, credit, law enforcement, safety components, etc.)
        │
        ▼
  Check Article 52 transparency obligations
  (chatbots, emotion recognition, synthetic content)
        │
        ▼
  Return RiskClassificationResponse
  + save RiskAssessment to DB
  + update AISystem.risk_level
```

### RAG query flow

```
POST /api/v1/rag/query
        │
        ▼
  JWT auth check
        │
        ▼
  load_vector_store()
  (raises 503 if FAISS index not built yet)
        │
        ▼
  FAISS semantic search (k=5 chunks)
        │
        ▼
  LangChain RetrievalQA.run(question, context_chunks)
        │
        ▼
  Return answer + source_documents metadata
```

---

## Database schema

```
users
  id (PK)
  email (unique)
  hashed_password
  full_name
  company_name
  subscription_tier          ENUM(free, starter, growth, scale)
  stripe_customer_id
  stripe_subscription_id
  is_active
  created_at / updated_at

ai_systems
  id (PK)
  owner_id (FK → users)
  name
  description
  version
  use_case
  sector
  risk_level                 ENUM(minimal, limited, high, unacceptable)
  compliance_status          ENUM(not_started, in_progress, compliant, non_compliant)
  questionnaire_responses    JSON
  created_at / updated_at

risk_assessments
  id (PK)
  ai_system_id (FK → ai_systems)
  assessment_type
  risk_level
  findings                   JSON
  recommendations            JSON
  overall_score              Float
  assessed_at

documents
  id (PK)
  owner_id (FK → users)
  ai_system_id (FK → ai_systems)
  title
  document_type              ENUM(technical_documentation, risk_assessment,
                                  conformity_declaration, data_governance,
                                  transparency_notice, ...)
  status                     ENUM(draft, generated, approved, archived)
  content                    Text (Markdown)
  file_path                  nullable (PDF path)
  created_at / updated_at
```

---

## Authentication flow

```
POST /api/v1/auth/register  →  hash password (bcrypt)  →  store user  →  201
POST /api/v1/auth/login     →  verify password  →  issue JWT (30min expiry)  →  200
GET  /api/v1/auth/me        →  decode JWT  →  load user  →  200

All protected routes:
  Authorization: Bearer <token>
      │
      ▼
  get_current_user() dependency
      │
      ▼
  python-jose JWT decode  →  load User from DB
      │
      ├── Invalid token  →  401
      └── Valid          →  inject User into route handler
```

**JWT payload:**
```json
{"sub": "user@example.com", "exp": 1234567890}
```

---

## Directory structure

```
AegisAI/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── __init__.py          ← router registration
│   │   │       ├── auth.py              ← register, login, /me
│   │   │       ├── ai_systems.py        ← CRUD for AI system registry
│   │   │       ├── classification.py    ← EU AI Act risk classification
│   │   │       ├── documents.py         ← compliance document generation
│   │   │       ├── guard.py             ← prompt injection scan endpoint
│   │   │       └── rag.py               ← regulatory Q&A endpoint
│   │   ├── core/
│   │   │   ├── config.py                ← pydantic-settings (reads .env)
│   │   │   ├── database.py              ← SQLAlchemy engine + session
│   │   │   └── security.py             ← JWT encode/decode, bcrypt, get_current_user
│   │   ├── models/
│   │   │   ├── user.py                  ← User ORM model
│   │   │   ├── ai_system.py             ← AISystem, RiskAssessment ORM models
│   │   │   └── document.py              ← Document ORM model
│   │   ├── schemas/
│   │   │   ├── user.py                  ← UserCreate, UserResponse, Token
│   │   │   ├── ai_system.py             ← RiskClassificationRequest/Response
│   │   │   └── document.py              ← DocumentGenerateRequest/Response
│   │   ├── modules/
│   │   │   ├── guard/
│   │   │   │   ├── __init__.py          ← exports RegexFilter, IntentClassifier, etc.
│   │   │   │   ├── guard_config.py      ← paths, thresholds, model config
│   │   │   │   ├── regex_rules.py       ← Layer 1: regex heuristics
│   │   │   │   ├── intent_classifier.py ← Layer 2: DeBERTa-v3 classifier
│   │   │   │   ├── decision_engine.py   ← Layer 3: combine signals
│   │   │   │   ├── sanitizer.py         ← Layer 4: remove meta-instructions
│   │   │   │   ├── llm_guard.py         ← orchestrator
│   │   │   │   └── train.py             ← CLI training script
│   │   │   ├── rag/
│   │   │   │   ├── document_loader.py   ← PDF loading + chunking
│   │   │   │   ├── vector_store.py      ← FAISS build + load
│   │   │   │   ├── retrieval_chain.py   ← LangChain RetrievalQA
│   │   │   │   └── ml_flow.py           ← MLflow tracking stub
│   │   │   └── llm/
│   │   │       └── llm_client.py        ← OpenAI-compatible LLM wrapper
│   │   └── main.py                      ← FastAPI app, CORS, router mount
│   ├── data/
│   │   ├── prompts.csv                  ← Guard classifier training data
│   │   └── regulatory_docs/             ← RAG source PDFs (add yours here)
│   ├── tests/
│   │   └── test_guard.py                ← Guard module test suite
│   ├── .env.example
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── AISystems.tsx
│   │   │   ├── Classification.tsx
│   │   │   ├── Documents.tsx
│   │   │   ├── Login.tsx
│   │   │   └── Register.tsx
│   │   ├── components/
│   │   │   └── Layout.tsx               ← sidebar + nav
│   │   ├── services/
│   │   │   └── api.ts                   ← axios instance + all API calls
│   │   ├── stores/
│   │   │   └── authStore.ts             ← Zustand auth state
│   │   ├── App.tsx                      ← routes + PrivateRoute wrapper
│   │   └── main.tsx                     ← React root + QueryClient
│   ├── Dockerfile
│   └── package.json
├── infra/
│   ├── deployment.yaml                  ← Kubernetes Deployment + Service + PVC + ConfigMap
│   ├── hpa.yaml                         ← HorizontalPodAutoscaler (CPU + memory)
│   └── Dockerfile.rag                   ← separate RAG container (optional)
├── notebooks/
│   └── train_guard_classifier.ipynb     ← Colab fine-tuning notebook
├── docs/
│   ├── getting-started.md
│   ├── architecture.md                  ← this file
│   ├── api-reference.md
│   ├── guard-module.md
│   └── rag-module.md
├── .github/
│   ├── workflows/ci.yml                 ← backend tests + frontend build
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
├── docker-compose.yml
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── CHANGELOG.md
└── README.md
```

---

## Key design decisions

### 1. OpenAI-compatible LLM client
Both the Guard module (prompt responses) and the RAG module (QA chain) use a single `LLMClient` that speaks the OpenAI chat-completions API. This means the provider is swappable with a single `.env` change — OpenAI, Ollama, Groq, Together AI, vLLM, or LM Studio all work without any code changes.

### 2. Four-layer Guard pipeline
Each layer has a different cost/coverage tradeoff:
- Regex is near-zero latency and catches obvious patterns
- DeBERTa catches semantically obfuscated attacks regex misses
- The decision engine is pure logic — easy to audit and modify thresholds
- The sanitizer preserves user intent while stripping hostile meta-instructions

The pipeline is fail-safe: if the ML model fails to load, it falls back to the pre-trained DeBERTa base rather than disabling the Guard entirely.

### 3. AGPL-3.0 licence
AGPL ensures that companies running AegisAI as a hosted service must release their modifications. This is intentional — it prevents closed-source forks while keeping it free for self-hosted deployments and contributions.

### 4. Module isolation
Each of the three modules (Compliance, Guard, RAG) can be used independently. The Guard module has no database dependency and can be imported and used outside the web server context. The RAG module requires only a FAISS index and an LLM API key.
