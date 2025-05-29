```bash
swarmcraft/
├── pyproject.toml
├── README.md
├── docker-compose.yml
├── .env.example
├── requirements.txt
├── src/
│   └── swarmcraft/
│       ├── __init__.py
│       ├── main.py                 # FastAPI app entry
│       ├── api/
│       │   ├── __init__.py
│       │   ├── routes.py           # API endpoints
│       │   └── websocket.py        # WebSocket handlers
│       ├── core/
│       │   ├── __init__.py
│       │   ├── swarm_base.py       # Base SwarmOptimizer class
│       │   ├── pso.py              # PSO implementation
│       │   └── loss_functions.py   # Rastrigin, custom functions
│       ├── models/
│       │   ├── __init__.py
│       │   ├── session.py          # Session/room models
│       │   └── participant.py     # User/participant models
│       ├── database/
│       │   ├── __init__.py
│       │   ├── sqlite_db.py        # SQLite operations
│       │   └── redis_client.py     # Redis operations
│       └── config.py               # Settings/configuration
└── frontend/                       # Future Svelte app
    └── (Phase 2)
```
