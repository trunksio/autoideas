# AutoIdeas Platform

A dual-purpose voice-driven platform for workshop ideation and research surveys, powered by ElevenLabs conversational AI.

## Overview

AutoIdeas provides two main applications:

1. **Think Tank** - Collects workshop ideas via voice conversation and visualizes them on Miro boards in real-time
2. **Healthcare AI Survey** - Conducts structured voice-based research surveys with PostgreSQL persistence and admin dashboard

Both systems use ElevenLabs voice agents for natural conversation and share common infrastructure (Redis queuing, Docker orchestration, Apache reverse proxy).

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              THINK TANK                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────┐    ┌─────────────┐    ┌───────┐    ┌────────┐    ┌──────────┐│
│  │ Frontend │───▶│ ElevenLabs  │───▶│  API  │───▶│ Redis  │───▶│  Worker  ││
│  │ + Miro   │    │ Voice Agent │    │       │    │ Queue  │    │          ││
│  └──────────┘    └─────────────┘    └───────┘    └────────┘    └────┬─────┘│
│       ▲                                                              │      │
│       │                                                              ▼      │
│       │                                                        ┌──────────┐ │
│       └────────────────────────────────────────────────────────│ Miro API │ │
│                                                                └──────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           HEALTHCARE AI SURVEY                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────┐    ┌─────────────┐    ┌───────┐    ┌────────┐    ┌──────────┐│
│  │ Landing  │───▶│ ElevenLabs  │───▶│  API  │───▶│ Redis  │───▶│  Survey  ││
│  │  Page    │    │ Voice Agent │    │       │    │ Queue  │    │  Worker  ││
│  └──────────┘    └─────────────┘    └───────┘    └────────┘    └────┬─────┘│
│                                                                      │      │
│  ┌──────────┐    ┌─────────────┐                                    ▼      │
│  │  Admin   │◀───│   Survey    │◀──────────────────────────────┌──────────┐│
│  │Dashboard │    │     API     │                               │PostgreSQL││
│  └──────────┘    └─────────────┘                               └──────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

## Features

### Think Tank
- **Voice Collection**: Natural conversation interface via ElevenLabs
- **Theme-Based Routing**: Ideas categorized into 4 workshop themes
- **Real-time Visualization**: Auto-populated Miro boards with color-coded sticky notes
- **Live Updates**: Server-Sent Events for real-time status

### Healthcare AI Survey
- **Structured Interviews**: 17 questions across 7 sections
- **Anonymous Collection**: Track by conversation ID only
- **Auto-Completion**: Sessions marked complete on final question
- **Admin Dashboard**: View sessions, answers, and export data
- **Export Options**: CSV and JSON formats

## Quick Start

### Prerequisites

- Docker and Docker Compose
- ElevenLabs API key and configured agents
- Miro API key and board access (for Think Tank)
- Apache with SSL (for production)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd autoideas
```

2. Create environment file:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Start the services:
```bash
docker-compose up -d
```

4. Access the applications:

| Application | Local URL | Production URL |
|------------|-----------|----------------|
| Think Tank UI | http://localhost:3001 | https://apps.equalexperts.ai/thinktank |
| Survey Landing | http://localhost:3005 | https://apps.equalexperts.ai/survey |
| Survey Admin | http://localhost:3004 | https://apps.equalexperts.ai/survey/admin |
| API | http://localhost:8080 | https://apps.equalexperts.ai/thinktank/api |

## Services

| Service | Port | Purpose |
|---------|------|---------|
| `redis` | 6379 | Job queue and caching |
| `postgres` | 5432 (internal) | Survey data persistence |
| `api` | 8080 | Webhook handler + Survey API |
| `frontend` | 3001 | Think Tank UI |
| `worker` | - | Think Tank job processor |
| `survey-worker` | - | Survey answer processor |
| `survey-admin` | 3004 | Admin dashboard |
| `survey-frontend` | 3005 | Survey landing page |

## API Endpoints

### Think Tank Webhooks

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/webhook` | POST | ElevenLabs idea submission | X-API-Key |
| `/webhook/raw` | POST | Debug endpoint | X-API-Key |
| `/queue/status` | GET | Check queue status | X-API-Key |
| `/` | GET | Health check | None |

### Survey API

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/webhook/survey` | POST | ElevenLabs answer submission | X-API-Key |
| `/survey/sessions` | GET | List all sessions with stats | None* |
| `/survey/sessions/{id}` | GET | Get session details | None* |
| `/survey/export` | GET | Export data (CSV/JSON) | None* |

*Admin endpoints protected by Apache Basic Auth in production

## Configuration

### Environment Variables

```bash
# Redis
REDIS_URL=redis://redis:6379

# PostgreSQL
DATABASE_URL=postgresql://survey:survey_dev@postgres:5432/survey
POSTGRES_PASSWORD=survey_dev

# API Security
AUTOIDEAS_API_KEY=your_webhook_api_key

# ElevenLabs
ELEVENLABS_API_KEY=your_key

# Miro (Think Tank only)
MIRO_API_KEY=your_key
MIRO_BOARD_ID=your_board_id

# OpenAI (optional - for enhanced processing)
OPENAI_API_KEY=your_key
```

### Workshop Configuration

Each workshop in `/configs/workshops/{workshop-id}/` requires:

```
workshop-id/
├── metadata.json           # Workshop details
├── elevenlabs/
│   ├── agent_config.json   # Agent settings
│   ├── system_prompt.txt   # Agent personality
│   └── questions.json      # Question flow
└── miro/
    ├── board_template.json # Board layout
    └── card_template.json  # Card styling
```

### ElevenLabs Agent Configuration

**Think Tank Agent ID**: `agent_9901k4jby1pbf7przmt61zskpkfe`
**Survey Agent ID**: `agent_9001ke7763raes091jpa7tm6ybrg`

See `/survey/elevenlabs-agent-prompt.md` for the survey agent system prompt and `/survey/elevenlabs-tool-config.md` for tool configuration.

## Database Schema

### Survey Tables

```sql
-- Sessions table
CREATE TABLE survey_sessions (
    id UUID PRIMARY KEY,
    conversation_id VARCHAR(255) UNIQUE NOT NULL,
    survey_id VARCHAR(100) DEFAULT 'healthcare_ai_2025',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB
);

-- Answers table
CREATE TABLE survey_answers (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES survey_sessions(id),
    question_id VARCHAR(100) NOT NULL,
    section_name VARCHAR(100),
    question_text TEXT,
    answer_type VARCHAR(50),  -- 'free_text', 'rating', 'multiple_choice'
    answer_text TEXT,
    answer_rating INTEGER CHECK (1-5),
    answer_choices JSONB,
    raw_transcript TEXT,
    answered_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(session_id, question_id)
);
```

## Development

### Local Development

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f api
docker-compose logs -f worker
docker-compose logs -f survey-worker

# Rebuild after changes
docker-compose build --no-cache <service>
docker-compose up -d <service>

# Scale workers
docker-compose up -d --scale worker=4
```

### Useful Commands

```bash
# Check Redis queue
docker exec -it autoideas-redis-1 redis-cli
> LLEN miro_card
> LLEN survey_queue

# Check PostgreSQL
docker exec -it autoideas-postgres-1 psql -U survey -d survey
> SELECT COUNT(*) FROM survey_sessions;
> SELECT * FROM survey_answers LIMIT 10;

# Check worker status
docker exec -it autoideas-worker-1 rq info
```

## Production Deployment

### Apache Reverse Proxy

The Apache configuration (`/apache/apps.equalexperts.ai-le-ssl.conf`) routes:

| Path | Destination | Auth |
|------|-------------|------|
| `/thinktank/api` | localhost:8080 | X-API-Key |
| `/thinktank` | localhost:3001 | Basic Auth |
| `/survey/api` | localhost:8080 | X-API-Key |
| `/survey/admin` | localhost:3004 | Basic Auth |
| `/survey` | localhost:3005 | None (public) |
| `/awdio/*` | localhost:8002/3003 | OAuth/JWT |

### Deploy Steps

```bash
# Build images
docker-compose build

# Deploy
docker-compose up -d

# Copy Apache config
sudo cp apache/apps.equalexperts.ai-le-ssl.conf /etc/apache2/sites-available/
sudo apache2ctl configtest
sudo systemctl reload apache2
```

### Authentication

- **Think Tank UI**: HTTP Basic Auth (`.htpasswd-thinktank`)
- **Survey Admin**: HTTP Basic Auth (`.htpasswd-survey`)
- **Webhooks**: X-API-Key header validation
- **Survey Landing**: Public (no auth)

## Project Structure

```
autoideas/
├── api/                    # FastAPI webhook handler + Survey API
│   └── src/main.py
├── workers/                # Think Tank job processor
│   └── src/
│       ├── worker.py
│       ├── triage_agent.py
│       ├── miro_client.py
│       └── ai_processor.py
├── survey-worker/          # Survey answer processor
│   └── src/
│       ├── worker.py
│       └── survey_processor.py
├── frontend/               # Think Tank UI
│   ├── index.html
│   └── css/styles.css
├── survey-frontend/        # Survey landing page
│   ├── index.html
│   └── css/styles.css
├── survey-admin/           # Admin dashboard
│   ├── index.html
│   ├── js/app.js
│   └── css/styles.css
├── db/init/                # PostgreSQL schema
├── configs/workshops/      # Workshop configurations
├── apache/                 # Reverse proxy config
├── survey/                 # ElevenLabs documentation
│   ├── elevenlabs-agent-prompt.md
│   └── elevenlabs-tool-config.md
├── docker-compose.yml
├── EEStyle.md              # Brand guidelines
└── CLAUDE.md               # Developer guidelines
```

## Troubleshooting

### Common Issues

1. **Voice agent not loading**
   - Check ElevenLabs agent ID in HTML
   - Verify browser microphone permissions
   - Check browser console for errors

2. **Ideas not appearing on Miro**
   - Verify `MIRO_API_KEY` and `MIRO_BOARD_ID`
   - Check worker logs: `docker-compose logs worker`
   - Verify board permissions in Miro

3. **Survey answers not saving**
   - Check `DATABASE_URL` in environment
   - Verify PostgreSQL is healthy: `docker-compose logs postgres`
   - Check survey-worker logs: `docker-compose logs survey-worker`

4. **Webhook errors (401/422)**
   - Verify `X-API-Key` header matches `AUTOIDEAS_API_KEY`
   - Check payload format matches expected schema
   - Review API logs: `docker-compose logs api`

5. **CSS/assets returning 403**
   - Rebuild container: `docker-compose build --no-cache <service>`
   - Check file permissions in Dockerfile (755 for dirs, 644 for files)

## Brand Guidelines

The survey applications follow Equal Experts brand guidelines (see `EEStyle.md`):

- **Primary Color**: EE Blue `#1795D4`
- **Headings**: Tech Blue `#22567C`
- **Body Text**: Dark Data `#212526`
- **Accent/CTA**: Ember `#F07C00`
- **Background**: Cloud `#F5F5F5`
- **Font**: Lexend (300/400/500/700 weights)

## Support

For issues and questions:
- Contact: matthew.waugh@equalexperts.com
- GitHub Issues: https://github.com/trunksio/autoideas/issues
