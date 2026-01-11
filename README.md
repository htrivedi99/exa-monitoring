# Internet Monitoring Application

Monitor the internet for new content using Exa AI and GPT-4. Create custom search queries and get notified when new, significant information appears.

## Features

- 🔍 **Smart Monitoring**: Create natural language queries to monitor specific topics
- 🤖 **AI-Powered Analysis**: GPT-4 analyzes new content for significance
- ⏰ **Flexible Schedules**: Check hourly, daily, weekly, or custom intervals
- 🔔 **Webhook Notifications**: Get alerts when important changes are detected
- 📊 **Results History**: View all historical data and source URLs
- 🎯 **URL Deduplication**: Automatically filters out previously seen content

## Architecture

- **Backend**: FastAPI (Python) with background scheduler
- **Frontend**: React + Vite
- **Storage**: Filesystem-based JSON (no database required)
- **APIs**: Exa AI for search, OpenAI GPT-4 for analysis
- **Deployment**: Docker containers

## Prerequisites

- Docker and Docker Compose
- API Keys:
  - [Exa API Key](https://exa.ai/)
  - [OpenAI API Key](https://platform.openai.com/)

## Quick Start

### 1. Clone and Setup

```bash
cd exa-monitoring

# Create environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### 2. Configure API Keys

Edit `backend/.env` and add your API keys:

```bash
EXA_API_KEY=your_exa_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run with Docker Compose

```bash
docker-compose up --build
```

### 4. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Usage

### Creating a Monitor

1. Click "Create New Monitor"
2. Enter your search query (e.g., "FDA diabetes drug approvals")
3. Select check frequency (hourly, daily, weekly, etc.)
4. Optionally add a webhook URL for notifications
5. Click "Create Monitor"

The monitor will:
- Run immediately upon creation
- Search for relevant content using Exa AI
- Extract and analyze content with GPT-4
- Save results and schedule future runs
- Send webhook notifications for significant changes

### Viewing Results

Click on any monitor card to view:
- Latest run results
- AI analysis summary
- Historical data with timestamps
- Source URLs for all findings
- Key changes detected

### Manual Runs

You can manually trigger a monitor run anytime by clicking "Run Now" on the monitor detail page.

## Project Structure

```
exa-monitoring/
├── backend/
│   ├── app/
│   │   ├── api/routes/         # API endpoints
│   │   ├── models/             # Pydantic models
│   │   ├── services/           # Business logic
│   │   │   ├── exa_client.py   # Exa API integration
│   │   │   ├── llm_client.py   # GPT-4 integration
│   │   │   ├── monitor_runner.py # Core execution engine
│   │   │   ├── storage.py      # JSON filesystem storage
│   │   │   └── webhook.py      # Webhook delivery
│   │   ├── scheduler/          # Background job scheduler
│   │   ├── config.py           # Configuration
│   │   └── main.py            # FastAPI app
│   ├── data/                   # Runtime data storage
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/               # API client
│   │   ├── components/        # React components
│   │   ├── hooks/             # React Query hooks
│   │   ├── pages/             # Page components
│   │   ├── styles/            # CSS styles
│   │   ├── App.jsx            # Root component
│   │   └── main.jsx           # Entry point
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.js
└── docker-compose.yml
```

## API Endpoints

### Monitors

- `POST /api/v1/monitors` - Create new monitor
- `GET /api/v1/monitors` - List all monitors
- `GET /api/v1/monitors/{id}` - Get single monitor
- `PUT /api/v1/monitors/{id}` - Update monitor
- `DELETE /api/v1/monitors/{id}` - Delete monitor
- `POST /api/v1/monitors/{id}/run` - Manually trigger run

### Results

- `GET /api/v1/monitors/{id}/results` - Get results for a monitor
- `GET /api/v1/monitors/{id}/results/{result_id}` - Get single result

## Development

### Backend Development

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

## Configuration

### Backend Environment Variables

```bash
EXA_API_KEY=required          # Exa API key
OPENAI_API_KEY=required       # OpenAI API key
LOG_LEVEL=INFO                # Logging level
CORS_ORIGINS=http://localhost:5173  # Allowed CORS origins
DATA_DIR=data                 # Data storage directory
```

### Frontend Environment Variables

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## How It Works

### Monitor Creation Flow

1. User creates monitor with query + cadence
2. Backend immediately kicks off first run (non-blocking)
3. Exa API searches for relevant content
4. GPT-4 analyzes new content for significance
5. Results saved to filesystem
6. Webhook sent if content is significant
7. Next run scheduled based on cadence

### Scheduler

- Background APScheduler checks every minute
- Runs monitors when `next_run_at <= now`
- Error handling ensures scheduler never crashes
- Each monitor updates independently

### URL Deduplication

- All seen URLs stored in monitor's `seen_urls` array
- New search results filtered against this array
- Only genuinely new content is processed
- Prevents duplicate analysis and notifications

## Deployment

### Railway / Render / Fly.io

1. Create two services:
   - **Backend**: Python service using `backend/Dockerfile`
   - **Frontend**: Static site using `frontend/Dockerfile`

2. Set environment variables in platform:
   ```
   EXA_API_KEY=your_key
   OPENAI_API_KEY=your_key
   CORS_ORIGINS=https://your-frontend-url.com
   ```

3. Mount persistent volume for `backend/data` directory

4. Configure frontend env var:
   ```
   VITE_API_BASE_URL=https://your-backend-url.com/api/v1
   ```

### Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Troubleshooting

### Monitor not running automatically

- Check scheduler logs: `docker-compose logs backend`
- Verify `next_run_at` is set correctly
- Ensure monitor status is "active"

### API connection errors

- Verify backend is running: http://localhost:8000/api/v1/health
- Check CORS configuration in backend `.env`
- Confirm frontend `VITE_API_BASE_URL` is correct

### No new content detected

- Check Exa API rate limits
- Verify query is not too specific
- Review `seen_urls` count (may have already tracked all content)

## Limitations

- **Single instance**: Scheduler won't work with multiple backend replicas (use Celery+Redis for scaling)
- **Filesystem storage**: No concurrent write protection (fine for single instance)
- **No authentication**: Single-user application (add Auth0/Clerk for multi-user)
- **Unbounded seen_urls**: Array grows over time (implement cleanup for long-running monitors)

## Future Enhancements

- PostgreSQL database for better querying and scalability
- Redis + Celery for distributed task queue
- WebSocket for real-time updates in UI
- User authentication and multi-tenancy
- Email notifications
- Export results (JSON/CSV)
- Monitor templates and presets
- Pause/resume functionality
- Cost tracking and API usage analytics

## License

MIT

## Support

For issues and questions, please open an issue on GitHub.

---

Built with ❤️ using Exa AI and GPT-4
