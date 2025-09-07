# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AutoIdeas is a voice-driven workshop ideation platform that collects and visualizes ideas using ElevenLabs conversational AI and Miro boards. The system is designed for multi-customer, multi-workshop use with configurable question sets and themes.

## Architecture

- **Frontend**: JavaScript/HTML with ElevenLabs voice agent and Miro board embeds
- **MCP Server**: Python/FastAPI with SSE support for real-time updates
- **Workers**: Python/RQ background processors for idea processing and Miro integration
- **Queue**: Redis for message queuing and session management
- **Configuration**: JSON-based workshop configurations in `/configs/workshops/`

## Key Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Scale workers
docker-compose up -d --scale worker=4

# Run tests
pytest

# Check worker status
docker exec -it autoideas-worker-1 rq info
```

## Development Workflow

1. **Python Development**: Use UV package manager (`uv pip install -e .`)
2. **API Testing**: Access Swagger docs at http://localhost:8000/docs
3. **Frontend Development**: Served via nginx container on port 3000
4. **Configuration Changes**: Edit files in `/configs/workshops/` - changes are live

## Project Structure

```
/mcp-server/     - MCP SSE server (Python/FastAPI)
/workers/        - Background processors (Python/RQ)
/frontend/       - Web interface (JS/HTML)
/configs/        - Workshop configurations
/redis/          - Redis configuration
```

## Key Integration Points

1. **ElevenLabs → MCP**: Voice transcriptions via POST to `/voice/message`
2. **MCP → Redis**: Task queuing for async processing
3. **Workers → Miro**: Card creation via Miro API
4. **Frontend → SSE**: Real-time updates via `/sse/events`

## Workshop Configuration

Each workshop requires:
- `metadata.json` - Workshop details
- `elevenlabs/agent_config.json` - Voice agent setup
- `elevenlabs/questions.json` - Question flow
- `miro/board_template.json` - Board layout
- `miro/card_template.json` - Card styling

## Common Tasks

- **Add new workshop**: Create directory in `/configs/workshops/` with required JSON files
- **Modify questions**: Edit `elevenlabs/questions.json` for the workshop
- **Change board layout**: Update `miro/board_template.json`
- **Debug processing**: Check worker logs with `docker-compose logs worker`

## Important Notes

- Always use Docker Compose for consistent development environment
- Redis data persists in volume; clear with `docker-compose down -v` if needed
- Frontend auto-reloads; backend requires container restart for code changes
- MCP server handles SSE connections; ensure proper CORS configuration