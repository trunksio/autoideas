# AutoIdeas System Architecture

## Table of Contents
- [System Overview](#system-overview)
- [Data Flow](#data-flow)
- [Component Interactions](#component-interactions)
- [Workshop Configuration](#workshop-configuration)
- [Deployment Architecture](#deployment-architecture)
- [Processing Pipeline](#processing-pipeline)
- [API Architecture](#api-architecture)

## System Overview

```mermaid
graph TB
    subgraph "Client Layer"
        UI[Web Frontend<br/>JavaScript/HTML]
        EL[ElevenLabs<br/>Voice Agent]
        MB[Miro Board<br/>Embed]
    end
    
    subgraph "Application Layer"
        MCP[MCP Server<br/>Python/FastAPI]
        SSE[SSE Events<br/>Real-time Updates]
    end
    
    subgraph "Processing Layer"
        RQ[Redis Queue]
        WK1[Worker 1<br/>Python/RQ]
        WK2[Worker 2<br/>Python/RQ]
        WKN[Worker N<br/>Python/RQ]
    end
    
    subgraph "Storage Layer"
        REDIS[(Redis<br/>Cache & Queue)]
        CONFIG[Configuration<br/>JSON Files]
    end
    
    subgraph "External Services"
        ELAPI[ElevenLabs API]
        MAPI[Miro API]
        OAPI[OpenAI API<br/>Optional]
    end
    
    UI --> MCP
    EL --> MCP
    UI --> SSE
    UI --> MB
    
    MCP --> RQ
    MCP --> REDIS
    MCP --> CONFIG
    
    RQ --> WK1
    RQ --> WK2
    RQ --> WKN
    
    WK1 --> REDIS
    WK1 --> MAPI
    WK1 --> OAPI
    
    SSE --> UI
    
    EL <--> ELAPI
    MB <--> MAPI
```

## Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant VA as Voice Agent
    participant FE as Frontend
    participant MCP as MCP Server
    participant RQ as Redis Queue
    participant W as Worker
    participant M as Miro API
    participant SSE as SSE Events
    
    U->>VA: Speaks idea
    VA->>VA: Transcribe speech
    VA->>MCP: POST /voice/message
    MCP->>MCP: Validate workshop
    MCP->>RQ: Queue task
    MCP-->>VA: Return job_id
    MCP->>SSE: Publish "idea_submitted"
    SSE-->>FE: Update status
    
    RQ->>W: Dequeue task
    W->>W: Process idea
    W->>W: Cluster & theme
    W->>M: Create card
    M-->>W: Card created
    W->>SSE: Publish "idea_processed"
    SSE-->>FE: Update board
    FE->>FE: Refresh Miro embed
```

## Component Interactions

```mermaid
graph LR
    subgraph "Frontend Container"
        HTML[index.html]
        JS[app.js]
        VA[voice-agent.js]
        CSS[styles.css]
        NGINX[Nginx Server]
    end
    
    subgraph "MCP Server Container"
        SRV[server.py]
        HAND[handlers.py]
        CONF[config.py]
        UV1[UV Package Manager]
    end
    
    subgraph "Worker Container"
        PROC[processor.py]
        MIRO[miro_client.py]
        AI[ai_processor.py]
        UV2[UV Package Manager]
    end
    
    subgraph "Redis Container"
        CACHE[Session Cache]
        QUEUE[Task Queue]
        PUBSUB[Pub/Sub Channel]
    end
    
    JS --> SRV
    VA --> SRV
    SRV --> QUEUE
    QUEUE --> PROC
    PROC --> MIRO
    PROC --> AI
    SRV --> PUBSUB
    PUBSUB --> JS
    HAND --> CACHE
    PROC --> CACHE
```

## Workshop Configuration

```mermaid
graph TD
    subgraph "Configuration Structure"
        ROOT[configs/workshops/]
        WS[workshop-id/]
        META[metadata.json]
        
        subgraph "ElevenLabs Config"
            EL[elevenlabs/]
            AGENT[agent_config.json]
            PROMPT[system_prompt.txt]
            QUEST[questions.json]
        end
        
        subgraph "Miro Config"
            MR[miro/]
            BOARD[board_template.json]
            CARD[card_template.json]
        end
        
        ROOT --> WS
        WS --> META
        WS --> EL
        EL --> AGENT
        EL --> PROMPT
        EL --> QUEST
        WS --> MR
        MR --> BOARD
        MR --> CARD
    end
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Docker Compose Network"
        subgraph "Frontend Service"
            FE[nginx:alpine<br/>Port: 3000]
        end
        
        subgraph "MCP Service"
            MCP[python:3.11-slim<br/>Port: 8000]
        end
        
        subgraph "Worker Service"
            W1[python:3.11-slim<br/>Replica 1]
            W2[python:3.11-slim<br/>Replica 2]
        end
        
        subgraph "Redis Service"
            RD[redis:7-alpine<br/>Port: 6379]
        end
        
        subgraph "Volumes"
            V1[redis_data]
            V2[configs<br/>read-only]
        end
    end
    
    FE -->|proxy| MCP
    MCP -->|publish| RD
    W1 -->|consume| RD
    W2 -->|consume| RD
    RD --> V1
    MCP --> V2
    W1 --> V2
    W2 --> V2
```

## Processing Pipeline

```mermaid
flowchart TD
    START([Voice Input]) --> TRANS[Transcribe]
    TRANS --> VALID{Valid<br/>Workshop?}
    VALID -->|No| ERROR1[Return Error]
    VALID -->|Yes| QUEUE[Queue Task]
    
    QUEUE --> WORK[Worker Picks Up]
    WORK --> LOAD[Load Config]
    LOAD --> PROC[Process Transcript]
    
    PROC --> CAT[Categorize]
    CAT --> EXTRACT[Extract Key Points]
    EXTRACT --> SENT[Analyze Sentiment]
    
    SENT --> AI{AI<br/>Available?}
    AI -->|Yes| ENHANCE[Enhance with AI]
    AI -->|No| BASIC[Basic Processing]
    
    ENHANCE --> CLUSTER
    BASIC --> CLUSTER[Cluster Ideas]
    
    CLUSTER --> THEME[Generate Themes]
    THEME --> CREATE[Create Miro Card]
    
    CREATE --> POS[Calculate Position]
    POS --> STYLE[Apply Styling]
    STYLE --> POST[Post to Miro]
    
    POST --> SUCCESS{Success?}
    SUCCESS -->|Yes| UPDATE[Update Session]
    SUCCESS -->|No| RETRY{Retry?}
    
    RETRY -->|Yes| POST
    RETRY -->|No| ERROR2[Log Error]
    
    UPDATE --> PUBLISH[Publish Event]
    PUBLISH --> END([Complete])
```

## API Architecture

```mermaid
graph LR
    subgraph "REST Endpoints"
        GET1[GET /]
        GET2[GET /workshops]
        GET3[GET /workshops/{id}]
        GET4[GET /status]
        POST1[POST /voice/message]
        POST2[POST /mcp/tools/{tool}]
    end
    
    subgraph "SSE Endpoints"
        SSE1[GET /sse/events]
    end
    
    subgraph "Event Types"
        E1[connected]
        E2[idea_submitted]
        E3[idea_processed]
        E4[processing_error]
        E5[session_updated]
    end
    
    subgraph "MCP Tools"
        T1[submit_idea]
    end
    
    POST1 --> E2
    POST2 --> T1
    T1 --> E2
    
    SSE1 --> E1
    SSE1 --> E2
    SSE1 --> E3
    SSE1 --> E4
    SSE1 --> E5
```

## Message Flow States

```mermaid
stateDiagram-v2
    [*] --> VoiceInput: User speaks
    VoiceInput --> Transcribed: ElevenLabs processes
    Transcribed --> Submitted: Send to MCP
    Submitted --> Queued: Added to Redis
    
    Queued --> Processing: Worker picks up
    Processing --> Categorizing: Determine type
    Categorizing --> Enriching: Add metadata
    Enriching --> Clustering: Group similar
    Clustering --> Creating: Make Miro card
    
    Creating --> Posted: Send to Miro
    Posted --> Completed: Update session
    Completed --> [*]: Notify frontend
    
    Processing --> Failed: Error occurs
    Failed --> Retrying: Attempt retry
    Retrying --> Processing: Retry logic
    Failed --> [*]: Max retries
```

## Session Management

```mermaid
graph TD
    subgraph "Session Lifecycle"
        NEW[New Session<br/>Generated UUID]
        ACTIVE[Active Session<br/>Collecting Ideas]
        IDLE[Idle Session<br/>No Activity]
        EXPIRED[Expired Session<br/>24h TTL]
    end
    
    subgraph "Session Data"
        ID[session_id]
        WID[workshop_id]
        USER[user_nickname]
        COUNT[idea_count]
        LAST[last_activity]
    end
    
    NEW --> ACTIVE
    ACTIVE --> IDLE
    IDLE --> ACTIVE
    IDLE --> EXPIRED
    
    ACTIVE --> ID
    ACTIVE --> WID
    ACTIVE --> USER
    ACTIVE --> COUNT
    ACTIVE --> LAST
```

## Error Handling Flow

```mermaid
flowchart TD
    ERROR[Error Occurs] --> TYPE{Error Type}
    
    TYPE -->|API| API_ERR[API Error]
    TYPE -->|Queue| QUEUE_ERR[Queue Error]
    TYPE -->|Process| PROC_ERR[Processing Error]
    TYPE -->|External| EXT_ERR[External Service]
    
    API_ERR --> LOG1[Log Error]
    QUEUE_ERR --> LOG2[Log Error]
    PROC_ERR --> LOG3[Log Error]
    EXT_ERR --> LOG4[Log Error]
    
    LOG1 --> RESP1[HTTP Response]
    LOG2 --> RETRY1{Retry?}
    LOG3 --> RETRY2{Retry?}
    LOG4 --> RETRY3{Retry?}
    
    RETRY1 -->|Yes| REQUEUE[Requeue Task]
    RETRY1 -->|No| DLQ[Dead Letter Queue]
    
    RETRY2 -->|Yes| REPROCESS[Reprocess]
    RETRY2 -->|No| NOTIFY1[Notify User]
    
    RETRY3 -->|Yes| WAIT[Wait & Retry]
    RETRY3 -->|No| FALLBACK[Use Fallback]
    
    RESP1 --> CLIENT[Client Handles]
    NOTIFY1 --> SSE[SSE Event]
    FALLBACK --> CONTINUE[Continue Processing]
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend | HTML/JS/CSS | User interface |
| Voice | ElevenLabs SDK | Voice interaction |
| Visualization | Miro Embed | Idea boards |
| API Server | FastAPI/Python | Request handling |
| Queue | Redis/RQ | Task management |
| Workers | Python/RQ | Background processing |
| AI | OpenAI/Scikit-learn | Idea enhancement |
| Container | Docker | Deployment |
| Package Mgmt | UV | Python dependencies |
| Web Server | Nginx | Static serving & proxy |

## Scaling Considerations

```mermaid
graph LR
    subgraph "Horizontal Scaling"
        LB[Load Balancer]
        MCP1[MCP Server 1]
        MCP2[MCP Server 2]
        MCPN[MCP Server N]
    end
    
    subgraph "Worker Scaling"
        WP[Worker Pool]
        W1[Worker 1]
        W2[Worker 2]
        W3[Worker 3]
        WN[Worker N]
    end
    
    subgraph "Redis Cluster"
        MASTER[Redis Master]
        SLAVE1[Redis Replica 1]
        SLAVE2[Redis Replica 2]
    end
    
    LB --> MCP1
    LB --> MCP2
    LB --> MCPN
    
    WP --> W1
    WP --> W2
    WP --> W3
    WP --> WN
    
    MASTER --> SLAVE1
    MASTER --> SLAVE2
```

## Security Architecture

```mermaid
graph TD
    subgraph "Security Layers"
        AUTH[Authentication<br/>API Keys]
        AUTHZ[Authorization<br/>Workshop Access]
        VAL[Validation<br/>Input Sanitization]
        ENC[Encryption<br/>TLS/HTTPS]
        AUDIT[Audit<br/>Logging]
    end
    
    subgraph "Protected Resources"
        API[API Endpoints]
        CONFIG[Configurations]
        KEYS[API Keys]
        DATA[Session Data]
    end
    
    AUTH --> API
    AUTHZ --> CONFIG
    VAL --> API
    ENC --> DATA
    AUDIT --> API
```