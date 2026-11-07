# MentorMuni Website Knowledge Assistant

An AI-powered chatbot that answers questions about MentorMuni using information retrieved from its website.

The application uses Retrieval-Augmented Generation (RAG) to retrieve relevant website content and generate context-aware answers with source references.

## 1. Technology Stack

### Frontend
- React
- TypeScript
- Vite
- React Markdown
- Remark GFM

### Backend
- Python
- FastAPI
- SQLAlchemy
- Alembic
- Google Gemini API
- Sentence Transformers

### Database and AI
- PostgreSQL
- pgvector
- `all-MiniLM-L6-v2` embedding model
- Gemini `gemini-3.5-flash-lite`

## 2. Project Structure

```text
website-knowledge-assistant/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       └── chat.py
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   └── rag/
│   │   │       └── answer_service.py
│   │   └── main.py
│   │
│   ├── alembic/
│   ├── venv/
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── public/
│   │   └── mentormuni-logo.png
│   ├── src/
│   │   ├── App.tsx
│   │   ├── App.css
│   │   └── index.css
│   ├── package.json
│   └── vite.config.ts
│
├── .env
└── README.md
```

*Note: This is the logical project layout. Some folders or files may vary depending on the latest implementation.*

## 3. Prerequisites

Install the following software before setting up the application.

| Software | Requirement |
|---|---|
| Python | 3.11 or compatible project-supported version |
| Node.js | 22 or later |
| npm | Installed with Node.js |
| PostgreSQL | Supported PostgreSQL version |
| pgvector | PostgreSQL vector extension |
| Git | Latest stable version |

Verify installations:

```powershell
python --version
node --version
npm.cmd --version
git --version
```

Verify PostgreSQL:

```powershell
psql --version
```

## 4. Clone the Repository

```powershell
git clone <GIT_REPOSITORY_URL>
```

Navigate to the project:

```powershell
cd website-knowledge-assistant
```

## 5. Database Setup

The application uses PostgreSQL with the pgvector extension to store and retrieve website embeddings.

### Step 5.1: Create the database

Connect to PostgreSQL:

```powershell
psql -U postgres
```

Create the database:

```sql
CREATE DATABASE mentormuni_knowledge;
```

Connect to the database:

```sql
\c mentormuni_knowledge
```

Enable pgvector:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Verify the extension:

```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
```

Exit PostgreSQL:

```sql
\q
```

**Important:** pgvector must be installed on the PostgreSQL server itself. Installing the Python `pgvector` package alone is not sufficient.

## 6. Backend Setup

Open a new PowerShell terminal.

Navigate to the backend:

```powershell
cd website-knowledge-assistant\backend
```

### Step 6.1: Create a Python virtual environment

```powershell
python -m venv venv
```

### Step 6.2: Activate the virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, use this for the current terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Activate again:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 6.3: Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### Step 6.4: Install backend dependencies

```powershell
python -m pip install -r requirements.txt
```

### Step 6.5: Configure environment variables

Create the backend environment file using the project's environment template, if provided.

The backend needs configuration for:

- PostgreSQL connection
- Gemini API authentication
- Embedding model configuration, if configurable
- Application settings

Example database connection format:

```text
postgresql+psycopg://USERNAME:PASSWORD@localhost:5432/mentormuni_knowledge
```

**Important:** Use the exact environment-variable names expected by `app/core/config.py` or the project's settings module.

Never commit `.env` files or API keys to Git.

### Step 6.6: Run database migrations

```powershell
alembic upgrade head
```

This applies the database schema migrations.

### Step 6.7: Verify backend imports

```powershell
python -c "from app.main import app; print('Backend import: PASSED')"
```

Verify the RAG service:

```powershell
python -c "from app.services.rag.answer_service import answer_question; print('RAG service import: PASSED')"
```

## 7. Website Knowledge Ingestion

The chatbot uses website content stored in PostgreSQL.

The knowledge ingestion process consists of:

1. Discovering website URLs through the sitemap.
2. Crawling and extracting website content.
3. Cleaning and splitting content into chunks.
4. Generating vector embeddings using `all-MiniLM-L6-v2`.
5. Saving website content and embeddings in PostgreSQL.
6. Making the content available for similarity search.

The initial ingestion completed successfully during development:

- 19 sitemap URLs discovered.
- 18 pages processed.
- 40 content chunks persisted.
- Embeddings generated for all chunks.

**For a new environment:** Run the project's existing ingestion/indexing entry point before testing the chatbot.

The exact command must be confirmed from the current ingestion scripts. Do not assume the database is populated simply because migrations have completed.

## 8. Start the Backend

From the backend directory, with the virtual environment activated:

```powershell
python -m uvicorn app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

Health endpoint:

Check the health endpoint exposed by the application through Swagger.

Keep this terminal running.

## 9. Frontend Setup

Open a second terminal.

Navigate to the frontend directory:

```powershell
cd website-knowledge-assistant\frontend
```

### Step 9.1: Install frontend dependencies

```powershell
npm.cmd install
```

### Step 9.2: Verify frontend dependencies

```powershell
npm.cmd list --depth=0
```

### Step 9.3: Start the frontend

```powershell
npm.cmd run dev
```

The frontend should be available at:

```text
http://localhost:5173/
```

The Vite development server proxies API requests to:

```text
http://127.0.0.1:8000
```

Keep this terminal running.

## 10. Access the Application

Once both servers are running, open:

```text
http://localhost:5173/
```

You should see the MentorMuni chatbot interface.

The application provides:

- MentorMuni-branded chatbot interface.
- Suggested questions.
- Natural-language conversations.
- Context-aware follow-up questions.
- Markdown-formatted responses.
- Clickable website source references.
- Loading indicators.
- Responsive layout.

## 11. API Details

### Chat API

**Endpoint**

```http
POST /api/v1/chat
```

**Example request**

```json
{
  "question": "How does MentorMuni help students prepare for placements?",
  "top_k": 5,
  "conversation_history": []
}
```

**Example contextual follow-up**

```json
{
  "question": "How much does it cost?",
  "top_k": 5,
  "conversation_history": [
    {
      "role": "user",
      "content": "How does MentorMuni help students prepare for placements?"
    },
    {
      "role": "assistant",
      "content": "MentorMuni helps students prepare through interview readiness and placement preparation services."
    }
  ]
}
```

The conversation history helps the AI interpret follow-up questions. Answers must still be grounded in retrieved website content.

**Example response structure**

```json
{
  "question": "How much does it cost?",
  "answer": "Answer generated using available website information.",
  "sources": [
    {
      "source_id": 1,
      "title": "MentorMuni",
      "url": "https://www.mentormuni.com"
    }
  ],
  "retrieved_chunks": 5
}
```

The response content and source count will depend on the retrieved information.

## 12. Testing

### Backend testing

Open Swagger:

```text
http://127.0.0.1:8000/docs
```

Find:

```text
POST /api/v1/chat
```

Select **Try it out** and submit:

```json
{
  "question": "What services does MentorMuni offer?",
  "top_k": 5,
  "conversation_history": []
}
```

Verify:

- HTTP 200 response.
- Answer is relevant to the question.
- Sources are returned where available.
- Unsupported information is not fabricated.

### Frontend testing

Open:

```text
http://localhost:5173/
```

Try the following conversation:

1. How does MentorMuni help students prepare for placements?
2. How much does it cost?
3. Is it available for individual students?

Verify that follow-up questions use previous conversation context.

Also test:

- Empty question submission.
- Long questions.
- API unavailable scenario.
- Questions unrelated to MentorMuni.
- Source links.
- Markdown formatting.

## 13. Common Troubleshooting

### PostgreSQL connection error

Verify that PostgreSQL is running:

```powershell
Get-Service *postgres*
```

Verify database connectivity:

```powershell
psql -U postgres -d mentormuni_knowledge
```

Check the database connection configuration.

### pgvector extension error

Connect to the application database:

```powershell
psql -U postgres -d mentormuni_knowledge
```

Run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Python module not found

Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Reinstall dependencies:

```powershell
python -m pip install -r requirements.txt
```

### Gemini API error

Verify that:

- The Gemini API key is configured on the backend.
- The key is valid.
- The configured model is available to the API project.
- The backend can reach the Gemini service.

Never expose the Gemini API key in frontend code.

### Frontend API connection error

Verify that the backend is running:

```text
http://127.0.0.1:8000/docs
```

Check the Vite proxy configuration in:

```text
frontend/vite.config.ts
```

### npm command blocked in PowerShell

Use:

```powershell
npm.cmd install
npm.cmd run dev
```

## 14. Git Guidelines

Before committing changes:

```powershell
git status
```

Review modified files:

```powershell
git diff
```

Add changes:

```powershell
git add .
```

Commit:

```powershell
git commit -m "Update MentorMuni chatbot"
```

Push:

```powershell
git push
```

Ensure that `.env`, virtual environments, `node_modules`, local database files, and generated secrets are excluded from Git.

## 15. Development Workflow

For normal local development, two terminals are required.

**Terminal 1: Backend**

```powershell
cd website-knowledge-assistant\backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

**Terminal 2: Frontend**

```powershell
cd website-knowledge-assistant\frontend
npm.cmd run dev
```

Open the application:

```text
http://localhost:5173/
```

## 16. Important Security Notes

- Never commit API keys or database passwords.
- Keep Gemini credentials exclusively on the backend.
- Restrict database access to authorized services.
- Configure CORS for trusted origins before production deployment.
- Add API rate limiting before public exposure.
- Validate and limit conversation history.
- Use HTTPS in production.
- Configure database backups and production monitoring.

## 17. Application URLs

| Component | Local URL |
|---|---|
| Frontend | http://localhost:5173/ |
| Backend | http://127.0.0.1:8000 |
| Swagger | http://127.0.0.1:8000/docs |
| Chat API | http://127.0.0.1:8000/api/v1/chat |

---

**Project:** MentorMuni Website Knowledge Assistant

**Purpose:** Answer user questions about MentorMuni using website-grounded AI responses and contextual conversations.

**Architecture:** React + FastAPI + PostgreSQL/pgvector + Gemini.