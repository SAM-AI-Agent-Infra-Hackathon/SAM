# Supabase LCA Data Fetcher

A Python project for connecting to Supabase and fetching joined data from `lca_filings` and `lca_worksites` tables. Designed with clean architecture principles and ready for integration with LangChain/LangGraph for AI-powered data querying.

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
