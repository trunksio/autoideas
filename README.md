# AutoIdeas - Workshop Ideation Platform

A voice-driven idea collection system for workshops, powered by ElevenLabs conversational AI and Miro collaborative boards.

## Overview

AutoIdeas enables organizations to collect, process, and visualize ideas from workshop participants using natural voice conversations. The system automatically processes submissions, clusters similar ideas, and creates visual representations on Miro boards.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Frontend   │────▶│  MCP Server  │────▶│    Redis    │
│  (JS/HTML)  │     │   (Python)   │     │    Queue    │
└─────────────┘     └──────────────┘     └─────────────┘
       │                    │                    │
       │                    │                    ▼
       ▼                    ▼            ┌─────────────┐
┌─────────────┐     ┌──────────────┐     │   Workers   │
│ ElevenLabs  │     │     SSE      │     │  (Python)   │
│    Agent    │     │   Events     │     └─────────────┘
└─────────────┘     └──────────────┘            │
       │                                         ▼
       │                                 ┌─────────────┐
       └────────────────────────────────▶│  Miro API   │
                                         └─────────────┘
```

## Features

- **Voice Collection**: Natural conversation interface via ElevenLabs
- **Real-time Processing**: Asynchronous idea processing with Redis Queue
- **Automatic Clustering**: AI-powered grouping of similar ideas
- **Visual Boards**: Auto-populated Miro boards with categorized ideas
- **Multi-Workshop Support**: Configurable for different workshops and customers
- **Live Updates**: Server-Sent Events for real-time status updates

## Quick Start

### Prerequisites

- Docker and Docker Compose
- ElevenLabs API key
- Miro API key and board access
- OpenAI API key (optional, for enhanced processing)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd AutoIdeas
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

4. Access the application:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Configuration

### Workshop Setup

Create a new workshop configuration in `configs/workshops/<workshop-id>/`:

1. **metadata.json** - Workshop details
2. **elevenlabs/agent_config.json** - Voice agent configuration
3. **elevenlabs/system_prompt.txt** - Agent personality and guidelines
4. **elevenlabs/questions.json** - Workshop questions
5. **miro/board_template.json** - Board layout configuration
6. **miro/card_template.json** - Card styling rules

### Environment Variables

```bash
# Redis
REDIS_URL=redis://redis:6379

# APIs
ELEVENLABS_API_KEY=your_key_here
MIRO_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here  # Optional

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

## Development

### Local Development

1. Install Python dependencies:
```bash
cd mcp-server
uv pip install -e .
```

2. Install worker dependencies:
```bash
cd workers
uv pip install -e .
```

3. Start Redis:
```bash
docker run -p 6379:6379 redis:7-alpine
```

4. Run services:
```bash
# Terminal 1 - MCP Server
cd mcp-server
uvicorn src.server:app --reload

# Terminal 2 - Worker
cd workers
rq worker autoideas --url redis://localhost:6379

# Terminal 3 - Frontend
cd frontend
python -m http.server 3000
```

### Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=src --cov-report=html
```

## API Endpoints

### Core Endpoints

- `GET /` - Health check
- `GET /workshops` - List available workshops
- `GET /workshops/{id}` - Get workshop details
- `POST /voice/message` - Submit voice transcription
- `GET /sse/events` - Subscribe to real-time events
- `GET /status` - Server status and statistics

### MCP Tool Endpoints

- `POST /mcp/tools/submit_idea` - Submit idea via MCP protocol

## Deployment

### Production Deployment

1. Update Docker images:
```bash
docker-compose build
```

2. Configure production environment:
```bash
cp .env.production .env
# Update with production values
```

3. Deploy with scaling:
```bash
docker-compose up -d --scale worker=4
```

### Monitoring

- Redis Commander: http://localhost:8081 (if enabled)
- Application logs: `docker-compose logs -f`
- Worker status: `docker exec -it autoideas_worker_1 rq info`

## Incremental Delivery Plan

### Phase 1: Foundation ✅
- Project structure
- Docker setup
- Basic MCP server
- Redis configuration
- Worker skeleton
- Frontend structure

### Phase 2: Core Integration (Next)
- ElevenLabs voice integration
- Message routing
- Miro API connection
- Basic card creation

### Phase 3: Multi-Workshop Support
- Dynamic configuration
- Workshop selection UI
- Prompt management

### Phase 4: Enhanced Processing
- AI clustering
- Theme generation
- Deduplication

### Phase 5: Production Ready
- Authentication
- Monitoring
- Admin interface
- Performance optimization

## Troubleshooting

### Common Issues

1. **Voice agent not loading**
   - Check ElevenLabs API key
   - Verify agent configuration
   - Check browser console for errors

2. **Ideas not appearing on board**
   - Verify Miro API key
   - Check board permissions
   - Review worker logs

3. **Connection issues**
   - Ensure Redis is running
   - Check Docker network
   - Verify port availability

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions:
- GitHub Issues: [repository-issues-url]
- Documentation: [docs-url]