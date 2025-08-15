# 🏆 Hackathon Finalist — AI Agent & Infra Hackathon 2025

**Built for the [AI Agent & Infra Hackathon 2025](https://devpost.com/) (Aug 12–14, 2025)**  
Finalist in the 36-hour competition hosted by Lux Capital, Modal, Cognition, AWS, and Ramp.  

# SAM – Immigration Chatbot (H‑1B/PERM) with Live Sources
![ezgif-3ce569fd8b8f7c](https://github.com/user-attachments/assets/d5f80499-3b03-4e11-a1bb-f1245d90d627)

SAM is an AI assistant for international students and workers navigating U.S. employment-based visas (H‑1B, PERM). It combines:

- Live website scraping (MyVisaJobs) for employer/university H‑1B petition data
- A modern dark-themed chat UI
- A Flask API backend with an immigration-aware agent
- Supabase-backed LCA/PERM data access and LangChain tools



This README describes the problem being solved, how SAM helps, how to run the app, and the technical architecture. The lower half retains detailed Supabase data-service docs.

## ❗ Problems Being Addressed (2025)

- **Complex, opaque H‑1B/PERM processes**: Strict timelines, lottery selection, confusing steps (LCA, I‑129, etc.).
- **Sponsorship job search friction**: Hard to find employers willing/able to sponsor amid higher costs and wage rules.
- **Uncertainty and limited access to clear info**: Changing procedures, XLSX disclosures, and administrative delays make self‑service hard.
- **Rising costs and legal complexity**: Higher filing fees and employer burden reduce entry‑level sponsorship opportunities.

## ✅ How SAM Helps

- **Centralizes actionable data**: Scrapes MyVisaJobs reports/employer pages and integrates Supabase LCA/PERM records.
- **Chatbot guidance with sources**: Clear answers with clickable source bubbles; prompts for missing details (e.g., your university).
- **Improves job match efficiency**: Surfaces real employers and schools with recent filings and petitions.
- **Supports visa pathway planning**: Tools for LCA+PERM queries; ready for LangChain agents to reason over options.

## ✨ Key Features

- **Live MyVisaJobs scraping**
  - Top H‑1B petitioners (FY2025)
  - Company‑specific counts (incl. FY2025 I‑129 outcomes when available)
  - University‑specific counts (FY‑aware; slug URL handling like `employer/university-michigan/`)
- **Modern chat UI**: Dark theme, macOS‑style window chrome, message bubbles, typing indicators, quick actions, source link bubbles.
- **Flask API backend**: `/api/chat` endpoint, structured responses, robust error handling.
- **Immigration‑aware agent**: Detects intents (e.g., “how many from my school last year?”) and fetches live + DB data.
- **Supabase data service**: Unified LCA/PERM methods; LangChain tools for combined queries.

## 🚀 Quick Start (Chat App)

### 1) Environment

Create `.env` with:

```
SUPABASE_URL=...
SUPABASE_SERVICE_ROLE_KEY=...
# Optional if using OpenAI models via your agent/orchestration
OPENAI_API_KEY=...
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Run the Flask app

```bash
python app.py
```

Open the printed local URL and use the chat interface.

## 🔌 API

- `POST /api/chat`
  - Body: `{ "message": "your question" }`
  - Returns: formatted text plus source links (UI renders as small bubbles)

## 🧱 Components (selected files)

- `app.py` – Flask server (serves UI and `/api/chat`)
- `chat_ui.html` – Dark themed web UI
- `src/immigration_main_agent.py` – Enhanced immigration agent
- `src/web_sources.py` – Live scrapers (top companies, company counts, school counts)
- `src/services/data_service.py` – Supabase LCA/PERM data service
- `src/langchain_tools.py` – LangChain tool definitions (LCA/PERM/combined)
- `src/immigration_agent.py`, `src/agent.py` – Orchestration helpers

---

## 🏗️ Project Structure

```
/
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── supabase_client.py      # Supabase client configuration
│   ├── services/
│   │   ├── __init__.py
│   │   └── data_service.py         # Data fetching services (sync & async)
│   ├── __init__.py
│   └── main.py                     # Main script with examples
├── requirements.txt                # Python dependencies
├── .env.example                   # Environment variables template
└── README.md                      # This file
```

## 🚀 Quick Start

### 1. Set up Environment Variables

Copy the example environment file and fill in your Supabase credentials:

```bash
cp .env.example .env
```

Edit `.env` with your actual Supabase credentials:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
```

**Where to find these credentials:**
- **SUPABASE_URL**: In your Supabase dashboard → Settings → API → Project URL
- **SUPABASE_SERVICE_ROLE_KEY**: In your Supabase dashboard → Settings → API → Service Role Key

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Script

```bash
cd src
python main.py
```

## 📊 Database Schema

This project expects two related tables in your Supabase database:

### `lca_filings` table
- `case_number` (primary key)
- `employer_name`
- `job_title`
- ... (other fields)

### `lca_worksites` table  
- `case_number` (foreign key referencing lca_filings.case_number)
- `worksite_city`
- `prevailing_wage`
- ... (other fields)

## 🔧 Usage Examples

### Basic Synchronous Usage

```python
from services.data_service import get_sample_joined_data

# Fetch 10 records (default)
data = get_sample_joined_data()

# Fetch specific number of records
data = get_sample_joined_data(limit=25)
```

### Asynchronous Usage (for AI agents)

```python
import asyncio
from services.data_service import get_sample_joined_data_async

async def main():
    data = await get_sample_joined_data_async(limit=15)
    return data

# Run async function
data = asyncio.run(main())
```

### Using DataService Class

```python
from services.data_service import DataService

# Initialize service
service = DataService()

# Fetch data
data = service.get_sample_joined_data(limit=20)

# Async version
async_data = await service.get_sample_joined_data_async(limit=20)
```

## 🤖 AI Integration Ready

This project is designed for easy integration with LangChain and LangGraph:

### Key Features for AI Integration:

1. **Async Support**: All data functions have async versions for use in agent loops
2. **Custom Query Execution**: `execute_custom_query()` methods for AI-generated SQL
3. **Structured Data**: Returns Python dictionaries ready for AI processing
4. **Error Handling**: Comprehensive logging and error handling
5. **Modular Design**: Easy to extend and integrate

### Example LangChain Integration:

```python
from langchain.tools import BaseTool
from services.data_service import DataService

class SupabaseQueryTool(BaseTool):
    name = "supabase_query"
    description = "Query LCA filings and worksite data"
    
    def _run(self, limit: int = 10):
        service = DataService()
        return service.get_sample_joined_data(limit)
    
    async def _arun(self, limit: int = 10):
        service = DataService()
        return await service.get_sample_joined_data_async(limit)
```

## 📋 SQL Query Used

The project executes this JOIN query to combine data from both tables:

```sql
SELECT f.case_number, f.employer_name, f.job_title, w.worksite_city, w.prevailing_wage
FROM lca_filings f
JOIN lca_worksites w ON f.case_number = w.case_number
LIMIT {limit};
```

## 🛠️ Development

### Requirements

- Python 3.11+
- Supabase account with LCA data tables
- Internet connection

### Dependencies

- `supabase==2.3.4` - Supabase Python client
- `python-dotenv==1.0.0` - Environment variable management

### Code Style

This project follows clean code principles:
- **Modular**: Separated concerns (config, services, main)
- **Documented**: Comprehensive docstrings and comments
- **Error Handling**: Proper exception handling and logging
- **Type Hints**: Full type annotations for better IDE support
- **Async Ready**: Both sync and async implementations

## 🔍 Troubleshooting

### Common Issues:

1. **Missing Environment Variables**
   ```
   ValueError: Missing required environment variables
   ```
   - Solution: Check your `.env` file has both `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`

2. **Connection Errors**
   ```
   Failed to create Supabase client
   ```
   - Solution: Verify your Supabase credentials and internet connection

3. **Table Not Found**
   ```
   relation "lca_filings" does not exist
   ```
   - Solution: Ensure your Supabase database has the required tables

4. **No Data Returned**
   - Solution: Check if your tables have data and the JOIN condition matches records

### Debug Mode

Enable detailed logging by setting the log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 Next Steps

1. **Add More Query Functions**: Extend `DataService` with domain-specific queries
2. **Build Web API**: Create FastAPI endpoints using these services
3. **Add LangChain Integration**: Build AI agents that can query your data
4. **Add Data Validation**: Implement Pydantic models for type safety
5. **Add Caching**: Implement Redis or in-memory caching for frequently accessed data

## 📝 License

This project is provided as-is for educational and development purposes.
